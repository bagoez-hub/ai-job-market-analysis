"""
kpi_analysis.py — Key Performance Indicator (KPI) calculations.

Covers analysis areas:
  - A1: Salary Trends and Benchmarks
      (overall salary stats, salary by experience / industry / job title / company size)
  - A3: Employment Dynamics and Company Profiles
      (employment type share, company size distribution, experience mix)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger()


# ---------------------------------------------------------------------------
# Salary KPIs (A1)
# ---------------------------------------------------------------------------


def _salary_stats(series: pd.Series) -> dict[str, float]:
    """Compute a standard set of salary statistics for a numeric series."""
    clean = series.dropna()
    if clean.empty:
        return {}
    return {
        "count": int(clean.count()),
        "mean": round(float(clean.mean()), 2),
        "median": round(float(clean.median()), 2),
        "std": round(float(clean.std()), 2),
        "min": round(float(clean.min()), 2),
        "max": round(float(clean.max()), 2),
        "p25": round(float(clean.quantile(0.25)), 2),
        "p75": round(float(clean.quantile(0.75)), 2),
    }


def salary_overall(df: pd.DataFrame, salary_col: str = "salary_avg") -> dict[str, float]:
    """
    Compute overall salary statistics across the entire dataset.

    Args:
        df: Enriched DataFrame.
        salary_col: Name of the numeric salary column.

    Returns:
        Dictionary of salary statistics.
    """
    if salary_col not in df.columns:
        logger.warning(f"salary_overall: '{salary_col}' not found")
        return {}
    return _salary_stats(df[salary_col])


def salary_by_group(
    df: pd.DataFrame,
    group_col: str,
    salary_col: str = "salary_avg",
) -> pd.DataFrame:
    """
    Compute salary statistics broken down by a categorical grouping column.

    Args:
        df: Enriched DataFrame.
        group_col: Column to group by (e.g. ``"experience_level"``).
        salary_col: Numeric salary column.

    Returns:
        DataFrame with one row per group and salary statistic columns.
    """
    if group_col not in df.columns or salary_col not in df.columns:
        logger.warning(f"salary_by_group: '{group_col}' or '{salary_col}' not found")
        return pd.DataFrame()

    agg = (
        df.dropna(subset=[salary_col])
        .groupby(group_col)[salary_col]
        .agg(
            count="count",
            mean="mean",
            median="median",
            std="std",
            min="min",
            max="max",
        )
        .round(2)
        .reset_index()
        .sort_values("median", ascending=False)
    )
    return agg


# ---------------------------------------------------------------------------
# Employment & company KPIs (A3)
# ---------------------------------------------------------------------------


def employment_type_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count and percentage share of postings per employment type.

    Args:
        df: Enriched DataFrame with an ``employment_type`` column.

    Returns:
        DataFrame with columns [employment_type, count, share_pct].
    """
    if "employment_type" not in df.columns:
        return pd.DataFrame()

    counts = df["employment_type"].value_counts().reset_index()
    counts.columns = ["employment_type", "count"]
    counts["share_pct"] = (counts["count"] / counts["count"].sum() * 100).round(2)
    return counts


def company_size_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count and percentage share of postings per company size tier.

    Args:
        df: Enriched DataFrame with a ``company_size`` column.

    Returns:
        DataFrame with columns [company_size, count, share_pct].
    """
    if "company_size" not in df.columns:
        return pd.DataFrame()

    order = ["Startup", "Mid", "Large"]
    counts = (
        df["company_size"]
        .value_counts()
        .reindex(order, fill_value=0)
        .reset_index()
    )
    counts.columns = ["company_size", "count"]
    counts["share_pct"] = (counts["count"] / counts["count"].sum() * 100).round(2)
    return counts


def experience_level_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count and percentage share of postings per experience level.

    Args:
        df: Enriched DataFrame with an ``experience_level`` column.

    Returns:
        DataFrame with columns [experience_level, count, share_pct].
    """
    if "experience_level" not in df.columns:
        return pd.DataFrame()

    order = ["Entry", "Mid", "Senior"]
    counts = (
        df["experience_level"]
        .value_counts()
        .reindex(order, fill_value=0)
        .reset_index()
    )
    counts.columns = ["experience_level", "count"]
    counts["share_pct"] = (counts["count"] / counts["count"].sum() * 100).round(2)
    return counts


# ---------------------------------------------------------------------------
# Full KPI orchestration
# ---------------------------------------------------------------------------


def calculate_kpis(df: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    """
    Compute all KPIs across salary benchmarks and employment dynamics.

    KPIs computed:
    - Overall salary statistics
    - Salary by experience level
    - Salary by industry
    - Salary by job title
    - Salary by company size
    - Employment type distribution
    - Company size distribution
    - Experience level distribution
    - Top 10 paying job titles (by median salary)

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.

    Returns:
        Dictionary of KPI DataFrames and scalar stats, keyed by topic.
    """
    logger.info("Calculating KPIs")
    salary_col = "salary_avg"

    kpis: dict[str, Any] = {
        "salary_overall": salary_overall(df, salary_col),
        "salary_by_experience": salary_by_group(df, "experience_level", salary_col),
        "salary_by_industry": salary_by_group(df, "industry", salary_col),
        "salary_by_job_title": salary_by_group(df, "job_title", salary_col),
        "salary_by_company_size": salary_by_group(df, "company_size", salary_col),
        "employment_type_distribution": employment_type_distribution(df),
        "company_size_distribution": company_size_distribution(df),
        "experience_level_distribution": experience_level_distribution(df),
    }

    # Top 10 paying job titles by median salary
    if not kpis["salary_by_job_title"].empty:
        kpis["top_paying_titles"] = (
            kpis["salary_by_job_title"]
            .nlargest(10, "median")[["job_title", "median", "count"]]
            .reset_index(drop=True)
        )
    else:
        kpis["top_paying_titles"] = pd.DataFrame()

    # Persist KPI tables
    tables_dir = Path(config.get("output", {}).get("tables_dir", "outputs/tables"))
    tables_dir.mkdir(parents=True, exist_ok=True)

    dataframe_kpis = {
        k: v for k, v in kpis.items() if isinstance(v, pd.DataFrame) and not v.empty
    }
    for name, frame in dataframe_kpis.items():
        out_path = tables_dir / f"kpi_{name}.csv"
        frame.to_csv(out_path, index=False)
        logger.debug(f"KPI table saved → {out_path}")

    logger.info(
        f"KPIs complete — overall median salary: "
        f"${kpis['salary_overall'].get('median', 'N/A'):,}"
    )
    return kpis
