"""
exploratory.py — Exploratory Data Analysis (EDA) module.

Covers analysis areas A1 and A4 (supporting role):
  - Summary statistics for numeric and categorical columns
  - Missing data profiling
  - Distribution analysis (salary, experience, employment type)
  - Full EDA orchestration
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger()


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------


def generate_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate descriptive statistics for all numeric columns.

    Args:
        df: Input DataFrame (cleaned or enriched).

    Returns:
        DataFrame of descriptive statistics (count, mean, std, min, percentiles, max).
    """
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        logger.warning("generate_summary_statistics: no numeric columns found")
        return pd.DataFrame()
    stats = numeric.describe().T
    stats["median"] = numeric.median()
    stats["skewness"] = numeric.skew()
    logger.debug(f"generate_summary_statistics: {len(stats)} numeric columns profiled")
    return stats


def generate_categorical_summary(df: pd.DataFrame) -> dict[str, pd.Series]:
    """
    Generate value-count tables for all categorical (object) columns.

    Args:
        df: Input DataFrame.

    Returns:
        Dictionary mapping column name to its value-count Series.
    """
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    result: dict[str, pd.Series] = {}
    for col in cat_cols:
        result[col] = df[col].value_counts(dropna=False)
    logger.debug(f"generate_categorical_summary: {len(result)} categorical columns profiled")
    return result


# ---------------------------------------------------------------------------
# Missing data analysis
# ---------------------------------------------------------------------------


def analyze_missing_data(df: pd.DataFrame) -> dict[str, Any]:
    """
    Profile missing values across all columns.

    Args:
        df: Input DataFrame.

    Returns:
        Dictionary with null counts, null percentages, total rows, and
        the count of rows containing at least one null.
    """
    total = len(df)
    null_counts = df.isnull().sum()
    null_pct = (null_counts / max(total, 1) * 100).round(2)
    rows_with_null = int(df.isnull().any(axis=1).sum())

    report: dict[str, Any] = {
        "total_rows": total,
        "rows_with_any_null": rows_with_null,
        "rows_with_any_null_pct": round(rows_with_null / max(total, 1) * 100, 2),
        "null_counts": null_counts.to_dict(),
        "null_percentages": null_pct.to_dict(),
        "columns_with_nulls": null_counts[null_counts > 0].index.tolist(),
    }
    logger.debug(
        f"analyze_missing_data: {len(report['columns_with_nulls'])} column(s) "
        f"have missing values"
    )
    return report


# ---------------------------------------------------------------------------
# Distribution helpers
# ---------------------------------------------------------------------------


def salary_distribution_summary(df: pd.DataFrame, salary_col: str = "salary_avg") -> dict[str, Any]:
    """
    Summarise the salary distribution statistics.

    Args:
        df: Enriched DataFrame with a numeric salary column.
        salary_col: Name of the salary column to summarise.

    Returns:
        Dictionary of salary statistics.
    """
    if salary_col not in df.columns:
        logger.warning(f"salary_distribution_summary: '{salary_col}' not found")
        return {}

    series = df[salary_col].dropna()
    if series.empty:
        return {}

    return {
        "count": int(series.count()),
        "mean": round(float(series.mean()), 2),
        "median": round(float(series.median()), 2),
        "std": round(float(series.std()), 2),
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "p25": round(float(series.quantile(0.25)), 2),
        "p75": round(float(series.quantile(0.75)), 2),
    }


def experience_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Return the count and share of postings per experience level.

    Args:
        df: DataFrame with an ``experience_level`` column.

    Returns:
        Value-count Series for experience level.
    """
    if "experience_level" not in df.columns:
        return pd.Series(dtype=int)
    return df["experience_level"].value_counts()


def posting_trend_by_month(df: pd.DataFrame, date_col: str = "posted_date") -> pd.Series:
    """
    Count job postings per calendar month.

    Args:
        df: Enriched DataFrame with a datetime ``date_col``.
        date_col: Name of the date column.

    Returns:
        Series indexed by month-period with posting counts.
    """
    if date_col not in df.columns:
        return pd.Series(dtype=int)
    monthly = (
        df.set_index(date_col)
        .resample("ME")
        .size()
        .rename("job_count")
    )
    return monthly


# ---------------------------------------------------------------------------
# Full EDA orchestration
# ---------------------------------------------------------------------------


def run_eda(df: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    """
    Execute a comprehensive exploratory analysis and optionally save
    summary tables to ``outputs/tables/``.

    Areas covered:
    - Numeric summary statistics
    - Categorical value distributions
    - Missing data profiling
    - Salary distribution summary
    - Experience level distribution
    - Monthly posting trend

    Args:
        df: Enriched (or cleaned) DataFrame.
        config: Loaded application configuration dictionary.

    Returns:
        Dictionary containing all EDA artefacts keyed by topic.
    """
    logger.info("Starting EDA")

    numeric_stats = generate_summary_statistics(df)
    cat_summary = generate_categorical_summary(df)
    missing = analyze_missing_data(df)
    salary_stats = salary_distribution_summary(df)
    exp_dist = experience_distribution(df)
    monthly_trend = posting_trend_by_month(df)

    report: dict[str, Any] = {
        "numeric_stats": numeric_stats,
        "categorical_summary": cat_summary,
        "missing_data": missing,
        "salary_distribution": salary_stats,
        "experience_distribution": exp_dist.to_dict(),
        "monthly_posting_trend": monthly_trend.to_dict(),
        "shape": {"rows": len(df), "columns": len(df.columns)},
    }

    # Persist summary tables when configured
    tables_dir = Path(config.get("output", {}).get("tables_dir", "outputs/tables"))
    tables_dir.mkdir(parents=True, exist_ok=True)

    if not numeric_stats.empty:
        numeric_stats.to_csv(tables_dir / "eda_numeric_stats.csv")
        logger.info(f"EDA numeric stats saved → {tables_dir / 'eda_numeric_stats.csv'}")

    exp_df = exp_dist.reset_index()
    exp_df.columns = ["experience_level", "count"]
    exp_df.to_csv(tables_dir / "eda_experience_distribution.csv", index=False)

    logger.info(
        f"EDA complete — {report['shape']['rows']:,} rows, "
        f"{report['shape']['columns']} columns; "
        f"{missing['rows_with_any_null']} rows with nulls"
    )
    return report
