from __future__ import annotations

import re
from typing import Any

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger()

# Reference date used for "days_since_posted" so results are deterministic
_REFERENCE_DATE = pd.Timestamp("2025-09-30")


# ---------------------------------------------------------------------------
# Salary feature extraction
# ---------------------------------------------------------------------------


def extract_salary_min(salary_str: str) -> float | None:
    """
    Extract the lower bound from a salary range string (e.g. ``"80000-120000"``).

    Args:
        salary_str: Raw salary range value.

    Returns:
        Minimum salary as float, or *None* when the pattern is not matched.
    """
    if not isinstance(salary_str, str):
        return None
    match = re.search(r"(\d+)", salary_str.replace(",", ""))
    return float(match.group(1)) if match else None


def extract_salary_max(salary_str: str) -> float | None:
    """
    Extract the upper bound from a salary range string (e.g. ``"80000-120000"``).

    Args:
        salary_str: Raw salary range value.

    Returns:
        Maximum salary as float, or *None* when the pattern is not matched.
    """
    if not isinstance(salary_str, str):
        return None
    match = re.search(r"-\s*(\d+)", salary_str.replace(",", ""))
    return float(match.group(1)) if match else None


def add_salary_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive ``salary_min``, ``salary_max``, and ``salary_avg`` columns from
    ``salary_range_usd``.

    Args:
        df: Cleaned DataFrame that contains a ``salary_range_usd`` column.

    Returns:
        New DataFrame with three additional salary columns.
    """
    result = df.copy()
    if "salary_range_usd" not in result.columns:
        logger.warning("add_salary_columns: 'salary_range_usd' column not found — skipped")
        return result

    result["salary_min"] = result["salary_range_usd"].apply(extract_salary_min)
    result["salary_max"] = result["salary_range_usd"].apply(extract_salary_max)

    valid_mask = result["salary_min"].notna() & result["salary_max"].notna()
    result.loc[valid_mask, "salary_avg"] = (
        result.loc[valid_mask, "salary_min"] + result.loc[valid_mask, "salary_max"]
    ) / 2

    logger.debug(
        f"add_salary_columns: populated salary_avg for "
        f"{valid_mask.sum():,}/{len(result):,} rows"
    )
    return result


# ---------------------------------------------------------------------------
# Skills / tools parsing
# ---------------------------------------------------------------------------


def parse_skills(
    df: pd.DataFrame,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Normalise ``skills_required`` and ``tools_preferred`` into clean lists
    stored as semicolon-separated strings.

    Also adds a ``skills_count`` column with the number of distinct skills
    listed per posting.

    Args:
        df: Cleaned DataFrame.
        config: Optional application config (reads ``features.skills.*``).

    Returns:
        DataFrame with normalised skill columns and ``skills_count``.
    """
    result = df.copy()
    max_skills: int = 10
    if config:
        max_skills = config.get("features", {}).get("skills", {}).get("max_skills", 10)

    def _normalize_list(raw: str | float, limit: int) -> str:
        if not isinstance(raw, str) or not raw.strip():
            return ""
        items = [s.strip().lower() for s in re.split(r"[,;|]", raw) if s.strip()]
        return ";".join(dict.fromkeys(items[:limit]))  # deduplicate, preserve order

    for col in ("skills_required", "tools_preferred"):
        if col in result.columns:
            result[col] = result[col].apply(lambda v: _normalize_list(v, max_skills))

    if "skills_required" in result.columns:
        result["skills_count"] = result["skills_required"].apply(
            lambda v: len(v.split(";")) if v else 0
        )

    return result


# ---------------------------------------------------------------------------
# Temporal feature engineering
# ---------------------------------------------------------------------------


def add_temporal_features(
    df: pd.DataFrame,
    date_col: str = "posted_date",
) -> pd.DataFrame:
    """
    Derive year, month, quarter, and days_since_posted from *date_col*.

    The reference date for ``days_since_posted`` is the dataset end date
    (2025-09-30) so results are deterministic regardless of when the
    pipeline runs.

    Args:
        df: DataFrame with a parsed datetime column named *date_col*.
        date_col: Name of the source datetime column.

    Returns:
        DataFrame with four additional temporal columns.
    """
    result = df.copy()
    if date_col not in result.columns:
        logger.warning(f"add_temporal_features: '{date_col}' not found — skipped")
        return result

    dt = result[date_col]
    result["posted_year"] = dt.dt.year
    result["posted_month"] = dt.dt.month
    result["posted_quarter"] = dt.dt.quarter
    result["days_since_posted"] = (_REFERENCE_DATE - dt).dt.days

    return result


# ---------------------------------------------------------------------------
# Experience level encoding
# ---------------------------------------------------------------------------


def encode_experience_level(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a numeric ``experience_order`` column (0 = Entry, 1 = Mid, 2 = Senior)
    to support ordinal analysis and regression.

    Args:
        df: DataFrame with an ``experience_level`` column.

    Returns:
        DataFrame with the additional ``experience_order`` column.
    """
    result = df.copy()
    order_map = {"Entry": 0, "Mid": 1, "Senior": 2}
    if "experience_level" in result.columns:
        result["experience_order"] = result["experience_level"].map(order_map)
    return result


# ---------------------------------------------------------------------------
# Orchestrated enrichment pipeline
# ---------------------------------------------------------------------------


def enrich_pipeline(
    cleaned_df: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    """
    Run the full enrichment pipeline according to *config*.

    Steps (all idempotent):
    1. Extract salary min / max / avg from ``salary_range_usd``
    2. Parse and normalise skills and tools columns
    3. Add temporal features from ``posted_date``
    4. Encode experience level as ordinal integer

    Args:
        cleaned_df: Cleaned DataFrame from :func:`~src.data.clean_data.clean_pipeline`.
        config: Loaded application configuration dictionary.

    Returns:
        Enriched DataFrame — original *cleaned_df* is never modified.
    """
    features_cfg = config.get("features", {})

    df = cleaned_df.copy()

    # Salary features
    salary_cfg = features_cfg.get("salary", {})
    if salary_cfg.get("extract_min", True) or salary_cfg.get("calculate_avg", True):
        df = add_salary_columns(df)

    # Skills / tools
    df = parse_skills(df, config)

    # Temporal features
    date_cfg = features_cfg.get("date", {})
    if any(
        date_cfg.get(k, True)
        for k in (
            "extract_year",
            "extract_month",
            "extract_quarter",
            "calculate_days_since_posted",
        )
    ):
        date_col: str = config.get("data", {}).get("date_columns", ["posted_date"])[0]
        df = add_temporal_features(df, date_col=date_col)

    # Ordinal encoding
    df = encode_experience_level(df)

    logger.info(
        f"enrich_pipeline complete — {len(df):,} rows, "
        f"{len(df.columns)} columns "
        f"(+{len(df.columns) - len(cleaned_df.columns)} new)"
    )
    return df

