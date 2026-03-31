from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from src.utils.logger import get_logger

logger = get_logger()

# ---------------------------------------------------------------------------
# Allowed categorical values (from analysis-instructions.md)
# ---------------------------------------------------------------------------

EXPERIENCE_LEVELS = ["Entry", "Mid", "Senior"]
EMPLOYMENT_TYPES = ["Full-time", "Contract", "Remote", "Internship"]
COMPANY_SIZES = ["Startup", "Mid", "Large"]
INDUSTRIES = [
    "Automotive",
    "E-commerce",
    "Education",
    "Finance",
    "Healthcare",
    "Retail",
    "Tech",
]

# ---------------------------------------------------------------------------
# Pydantic row schema
# ---------------------------------------------------------------------------


class JobRecordInput(BaseModel):
    """Pydantic v2 schema for a single raw job market row."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    job_id: int
    company_name: str = Field(min_length=1)
    industry: Literal[
        "Automotive",
        "E-commerce",
        "Education",
        "Finance",
        "Healthcare",
        "Retail",
        "Tech",
    ]
    job_title: str = Field(min_length=1)
    skills_required: str | None = None
    tools_preferred: str | None = None
    experience_level: Literal["Entry", "Mid", "Senior"]
    employment_type: Literal["Full-time", "Contract", "Remote", "Internship"]
    location: str | None = None
    salary_range_usd: str | None = None
    posted_date: datetime | date
    company_size: Literal["Startup", "Mid", "Large"]

    @field_validator("posted_date", mode="before")
    @classmethod
    def parse_posted_date(cls, v: Any) -> datetime:
        """Coerce strings and pandas Timestamps to datetime."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day)
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        if hasattr(v, "to_pydatetime"):  # pandas Timestamp
            return v.to_pydatetime()
        raise ValueError(f"Cannot parse posted_date: {v!r}")


def _validate_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Validate every row with the Pydantic schema.

    Returns:
        List of error dicts (empty when all rows pass).
    """
    errors: list[dict[str, Any]] = []
    records = df.where(df.notna(), other=None).to_dict(orient="records")

    for idx, record in enumerate(records):
        try:
            JobRecordInput.model_validate(record)
        except ValidationError as exc:
            for err in exc.errors():
                errors.append(
                    {
                        "row_index": idx,
                        "job_id": record.get("job_id"),
                        "field": ".".join(str(loc) for loc in err["loc"]),
                        "type": err["type"],
                        "message": err["msg"],
                    }
                )
    return errors


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


def validate_raw_data(
    df: pd.DataFrame,
    config: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Validate the raw DataFrame row-by-row with the Pydantic schema and
    apply business-rule checks.

    Args:
        df: Raw DataFrame loaded from CSV.
        config: Optional application config (used for quality thresholds).

    Returns:
        A tuple of (validated DataFrame, validation report dict).

    Raises:
        ValueError: When Pydantic row validation produces any errors.
        AssertionError: When a business-rule check fails.
    """
    thresholds: dict[str, Any] = {}
    if config:
        thresholds = config.get("validations", {}).get("quality_thresholds", {})

    min_completeness: float = thresholds.get("min_completeness", 0.80)
    max_duplicates: float = thresholds.get("max_duplicates", 0.01)

    report: dict[str, Any] = {
        "total_rows": len(df),
        "null_counts": df.isnull().sum().to_dict(),
        "duplicate_job_ids": int(df["job_id"].duplicated().sum()),
        "date_range": (
            str(df["posted_date"].min()),
            str(df["posted_date"].max()),
        ),
    }

    # -- Pydantic row validation --
    logger.info("Running Pydantic schema validation")
    row_errors = _validate_rows(df)
    if row_errors:
        report["schema_valid"] = False
        report["schema_errors"] = row_errors
        logger.error(f"Schema validation failed: {len(row_errors)} error(s)")
        raise ValueError(
            f"Pydantic validation failed with {len(row_errors)} error(s). "
            f"See report['schema_errors'] for details."
        )
    report["schema_valid"] = True

    # -- Business-rule checks --
    dup_ratio = report["duplicate_job_ids"] / max(len(df), 1)
    assert dup_ratio <= max_duplicates, (
        f"Duplicate job_id ratio {dup_ratio:.2%} exceeds threshold {max_duplicates:.2%}"
    )

    salary_completeness = df["salary_range_usd"].notna().mean()
    assert salary_completeness >= min_completeness, (
        f"salary_range_usd completeness {salary_completeness:.2%} "
        f"below minimum {min_completeness:.2%}"
    )

    report["business_rules_passed"] = True
    logger.info(
        f"Validation passed — {report['total_rows']:,} rows, "
        f"{report['duplicate_job_ids']} duplicates"
    )
    return df, report


def check_data_quality(
    df: pd.DataFrame,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Compute data-quality metrics without raising exceptions.

    Suitable for post-cleaning checks and monitoring dashboards.

    Args:
        df: DataFrame to inspect.
        config: Optional application config for thresholds.

    Returns:
        Dictionary of quality metrics including a top-level *passed* flag.
    """
    thresholds: dict[str, Any] = {}
    if config:
        thresholds = config.get("validations", {}).get("quality_thresholds", {})

    min_completeness: float = thresholds.get("min_completeness", 0.80)
    max_duplicates: float = thresholds.get("max_duplicates", 0.01)

    total = len(df)
    dup_count = int(df.get("job_id", pd.Series(dtype=int)).duplicated().sum())
    dup_ratio = dup_count / max(total, 1)
    completeness = {col: float(df[col].notna().mean()) for col in df.columns}
    overall_completeness = float(df.notna().mean().mean())

    passed = (dup_ratio <= max_duplicates) and (
        overall_completeness >= min_completeness
    )

    report: dict[str, Any] = {
        "passed": passed,
        "total_rows": total,
        "duplicate_ratio": dup_ratio,
        "overall_completeness": overall_completeness,
        "column_completeness": completeness,
        "null_counts": df.isnull().sum().to_dict(),
    }

    level = logger.info if passed else logger.warning
    level(
        f"Quality check {'passed' if passed else 'FAILED'} — "
        f"completeness: {overall_completeness:.2%}, "
        f"duplicates: {dup_ratio:.2%}"
    )
    return report

