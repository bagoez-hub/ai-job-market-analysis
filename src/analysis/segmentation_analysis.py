"""
segmentation_analysis.py — Segmentation and demand analysis.

Covers analysis areas:
  - A2: Technical Skill and Tool Demand
      (top skills, top tools, skill demand by experience / industry)
  - A3: Employment Dynamics and Company Profiles
      (experience mix cross-tabs, salary by company size segment)
  - A4: Geographic and Industry Demand
      (top hiring cities, salary by location, industry concentration)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger()


# ---------------------------------------------------------------------------
# Generic segmentation helpers
# ---------------------------------------------------------------------------


def segment_by_category(
    df: pd.DataFrame,
    group_cols: list[str],
    metrics: list[str],
) -> pd.DataFrame:
    """
    Group the DataFrame by *group_cols* and compute aggregated *metrics*.

    Supported metric names (applied to ``salary_avg`` where applicable):
    - ``"job_count"`` — count of postings per group
    - ``"mean_salary"`` — mean of ``salary_avg``
    - ``"median_salary"`` — median of ``salary_avg``

    Args:
        df: Enriched DataFrame.
        group_cols: Column(s) to group by.
        metrics: List of metric names to compute.

    Returns:
        Aggregated DataFrame sorted by ``job_count`` descending (if present).
    """
    valid_cols = [c for c in group_cols if c in df.columns]
    if not valid_cols:
        logger.warning(f"segment_by_category: none of {group_cols} found in df")
        return pd.DataFrame()

    grouped = df.groupby(valid_cols)
    agg_dict: dict[str, Any] = {}

    if "job_count" in metrics:
        result = grouped.size().reset_index(name="job_count")
    else:
        result = grouped.size().reset_index(name="_n")

    if "salary_avg" in df.columns:
        if "mean_salary" in metrics:
            mean_s = grouped["salary_avg"].mean().round(2).reset_index(name="mean_salary")
            result = result.merge(mean_s, on=valid_cols, how="left")
        if "median_salary" in metrics:
            med_s = grouped["salary_avg"].median().round(2).reset_index(name="median_salary")
            result = result.merge(med_s, on=valid_cols, how="left")

    sort_col = "job_count" if "job_count" in result.columns else result.columns[-1]
    return result.sort_values(sort_col, ascending=False).reset_index(drop=True)


def identify_top_segments(
    df: pd.DataFrame,
    by: str,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Return the top *top_n* rows of *df* sorted descending by column *by*.

    Args:
        df: Aggregated DataFrame (e.g. from :func:`segment_by_category`).
        by: Column name to rank by.
        top_n: Number of top rows to return.

    Returns:
        Subset DataFrame with the top *top_n* segments.
    """
    if by not in df.columns:
        logger.warning(f"identify_top_segments: '{by}' not found in df")
        return df.head(top_n)
    return df.nlargest(top_n, by).reset_index(drop=True)


# ---------------------------------------------------------------------------
# A2 — Skills and tools demand
# ---------------------------------------------------------------------------


def _explode_delimited(series: pd.Series, sep: str = ";") -> pd.Series:
    """
    Split a delimiter-separated series and explode into individual values.

    Args:
        series: Series of delimited strings (e.g. ``"python;sql;spark"``).
        sep: Delimiter character used in ``parse_skills`` (default: ``";"``)

    Returns:
        Flat Series of individual skill / tool strings.
    """
    return (
        series.dropna()
        .loc[lambda s: s != ""]
        .str.split(sep)
        .explode()
        .str.strip()
        .loc[lambda s: s != ""]
    )


def top_skills(
    df: pd.DataFrame,
    top_n: int = 20,
    col: str = "skills_required",
) -> pd.DataFrame:
    """
    Rank skills by frequency of occurrence across all job postings.

    Args:
        df: Enriched DataFrame with a semicolon-separated ``skills_required`` column.
        top_n: Number of top skills to return.
        col: Column name for skills (default: ``"skills_required"``).

    Returns:
        DataFrame with columns [skill, count, share_pct].
    """
    if col not in df.columns:
        logger.warning(f"top_skills: '{col}' not found")
        return pd.DataFrame()

    all_skills = _explode_delimited(df[col])
    counts = all_skills.value_counts().head(top_n).reset_index()
    counts.columns = ["skill", "count"]
    counts["share_pct"] = (counts["count"] / len(df) * 100).round(2)
    return counts


def top_tools(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Rank preferred tools by frequency across all job postings.

    Args:
        df: Enriched DataFrame with a semicolon-separated ``tools_preferred`` column.
        top_n: Number of top tools to return.

    Returns:
        DataFrame with columns [tool, count, share_pct].
    """
    if "tools_preferred" not in df.columns:
        logger.warning("top_tools: 'tools_preferred' not found")
        return pd.DataFrame()

    all_tools = _explode_delimited(df["tools_preferred"])
    counts = all_tools.value_counts().head(top_n).reset_index()
    counts.columns = ["tool", "count"]
    counts["share_pct"] = (counts["count"] / len(df) * 100).round(2)
    return counts


def skills_by_experience(
    df: pd.DataFrame,
    top_n_skills: int = 10,
) -> pd.DataFrame:
    """
    Show the most demanded skills for each experience level.

    Args:
        df: Enriched DataFrame.
        top_n_skills: Top N skills to surface per experience level.

    Returns:
        DataFrame with columns [experience_level, skill, count].
    """
    if "skills_required" not in df.columns or "experience_level" not in df.columns:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    for level, group in df.groupby("experience_level"):
        skill_counts = _explode_delimited(group["skills_required"]).value_counts().head(top_n_skills)
        for skill, cnt in skill_counts.items():
            rows.append({"experience_level": level, "skill": skill, "count": int(cnt)})
    return pd.DataFrame(rows)


def skills_by_industry(
    df: pd.DataFrame,
    top_n_skills: int = 10,
) -> pd.DataFrame:
    """
    Show the most demanded skills for each industry.

    Args:
        df: Enriched DataFrame.
        top_n_skills: Top N skills to surface per industry.

    Returns:
        DataFrame with columns [industry, skill, count].
    """
    if "skills_required" not in df.columns or "industry" not in df.columns:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    for industry, group in df.groupby("industry"):
        skill_counts = _explode_delimited(group["skills_required"]).value_counts().head(top_n_skills)
        for skill, cnt in skill_counts.items():
            rows.append({"industry": industry, "skill": skill, "count": int(cnt)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# A4 — Geographic and industry demand
# ---------------------------------------------------------------------------


def top_hiring_locations(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Rank locations by total posting count.

    Args:
        df: Enriched DataFrame with a ``location`` column.
        top_n: Number of top locations to return.

    Returns:
        DataFrame with columns [location, count, share_pct].
    """
    if "location" not in df.columns:
        return pd.DataFrame()

    counts = df["location"].value_counts().head(top_n).reset_index()
    counts.columns = ["location", "count"]
    counts["share_pct"] = (counts["count"] / len(df) * 100).round(2)
    return counts


def industry_posting_volume(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count postings and compute salary stats by industry.

    Args:
        df: Enriched DataFrame.

    Returns:
        DataFrame with columns [industry, job_count, mean_salary, median_salary].
    """
    if "industry" not in df.columns:
        return pd.DataFrame()

    cnt = df.groupby("industry").size().reset_index(name="job_count")
    if "salary_avg" in df.columns:
        sal = (
            df.groupby("industry")["salary_avg"]
            .agg(mean_salary="mean", median_salary="median")
            .round(2)
            .reset_index()
        )
        cnt = cnt.merge(sal, on="industry", how="left")
    return cnt.sort_values("job_count", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Full segmentation orchestration
# ---------------------------------------------------------------------------


def analyze_segments(df: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    """
    Run all segmentation analyses across skills demand, employment dynamics,
    and geographic / industry breakdowns.

    Segments computed:
    - Top 20 skills overall
    - Top 20 tools overall
    - Top 10 skills by experience level
    - Top 10 skills by industry
    - Job count + salary by experience level
    - Job count + salary by industry
    - Job count + salary by company size
    - Job count + salary by job title
    - Top 15 hiring locations
    - Industry posting volume + salary
    - Cross-tab: experience level × company size

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.

    Returns:
        Dictionary of segmentation DataFrames keyed by topic.
    """
    logger.info("Running segmentation analysis")
    seg_cfg = config.get("analysis", {}).get("segmentation", {})
    group_cols: list[str] = seg_cfg.get(
        "group_by", ["experience_level", "industry", "company_size", "job_title"]
    )
    metrics: list[str] = seg_cfg.get(
        "metrics", ["mean_salary", "median_salary", "job_count", "top_skills"]
    )

    segments: dict[str, Any] = {
        # A2 — Skills & tools
        "top_skills": top_skills(df, top_n=20),
        "top_tools": top_tools(df, top_n=20),
        "skills_by_experience": skills_by_experience(df, top_n_skills=10),
        "skills_by_industry": skills_by_industry(df, top_n_skills=10),
        # A3 — Employment dynamics segmentation
        **{
            f"by_{col}": segment_by_category(df, [col], metrics)
            for col in group_cols
            if col in df.columns
        },
        # A4 — Geographic & industry
        "top_hiring_locations": top_hiring_locations(df, top_n=15),
        "industry_posting_volume": industry_posting_volume(df),
    }

    # Cross-tab: experience × company size
    if "experience_level" in df.columns and "company_size" in df.columns:
        segments["crosstab_experience_company"] = segment_by_category(
            df, ["company_size", "experience_level"], ["job_count"]
        )

    # Persist tables
    tables_dir = Path(config.get("output", {}).get("tables_dir", "outputs/tables"))
    tables_dir.mkdir(parents=True, exist_ok=True)

    for name, frame in segments.items():
        if isinstance(frame, pd.DataFrame) and not frame.empty:
            out_path = tables_dir / f"seg_{name}.csv"
            frame.to_csv(out_path, index=False)
            logger.debug(f"Segment table saved → {out_path}")

    logger.info(
        f"Segmentation complete — {len(segments)} segment tables produced"
    )
    return segments
