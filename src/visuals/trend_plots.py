"""
trend_plots.py — Area 5: Hiring Velocity and Seasonality.

Covers analytical questions H-01 through H-05 from analysis-instructions.md:
  - Monthly posting volume trend (line)
  - Seasonal pattern — average postings by month (bar)
  - Industry posting volume by quarter (grouped bar)
  - Year-over-year growth by job title (bar)
  - Cumulative posting volume over time (area chart)
"""
from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

from src.visuals.plot_utils import apply_style, get_palette, save_figure
from src.utils.logger import get_logger

logger = get_logger()

_MONTH_ABBR = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def _require_temporal(df: pd.DataFrame, *cols: str) -> bool:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        logger.warning(f"Missing required columns: {missing}")
        return False
    return True


def plot_monthly_posting_volume(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Line chart of total job postings per calendar month.

    Addresses question H-01: month-over-month posting volume trend.

    Args:
        df: Enriched DataFrame with ``posted_date`` (datetime) or
            ``posted_year`` / ``posted_month`` columns.
        config: Loaded application configuration dictionary.
    """
    if not _require_temporal(df, "posted_year", "posted_month"):
        return

    df_copy = df.dropna(subset=["posted_year", "posted_month"]).copy()
    df_copy["year_month"] = (
        pd.to_datetime(
            df_copy["posted_year"].astype(int).astype(str)
            + "-"
            + df_copy["posted_month"].astype(int).astype(str).str.zfill(2)
        )
    )

    monthly = df_copy.groupby("year_month").size().reset_index(name="job_count")
    monthly = monthly.sort_values("year_month")

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(
        monthly["year_month"],
        monthly["job_count"],
        marker="o",
        linewidth=2,
        color=get_palette(config, 1)[0],
        markersize=4,
    )
    ax.fill_between(monthly["year_month"], monthly["job_count"], alpha=0.15)

    ax.set_title("Monthly Job Posting Volume")
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Postings")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    save_figure("monthly_posting_volume.png", config)
    plt.show()
    logger.info("plot_monthly_posting_volume complete")


def plot_seasonal_pattern(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Bar chart of average postings per calendar month across all years.

    Addresses question H-02: consistent seasonal patterns (peak months).

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    if not _require_temporal(df, "posted_month"):
        return

    df_copy = df.dropna(subset=["posted_month"]).copy()
    seasonal = (
        df_copy.groupby("posted_month")
        .size()
        .reset_index(name="job_count")
    )
    seasonal["month_name"] = seasonal["posted_month"].map(_MONTH_ABBR)

    fig, ax = plt.subplots()
    colors = get_palette(config, len(seasonal))
    ax.bar(seasonal["month_name"], seasonal["job_count"], color=colors)

    ax.set_title("Job Posting Volume by Month (Seasonal Pattern)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Postings")

    plt.tight_layout()
    save_figure("seasonal_pattern.png", config)
    plt.show()
    logger.info("plot_seasonal_pattern complete")


def plot_quarterly_volume_by_industry(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Grouped bar chart of quarterly posting volume per industry.

    Addresses question H-03: which industries post most in Q1 vs. Q3.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    if not _require_temporal(df, "posted_quarter", "industry"):
        return

    df_copy = df.dropna(subset=["posted_quarter", "industry"]).copy()
    pivot = (
        df_copy.groupby(["posted_quarter", "industry"])
        .size()
        .unstack(fill_value=0)
    )
    pivot.index = [f"Q{int(q)}" for q in pivot.index]

    fig, ax = plt.subplots(figsize=(12, 5))
    pivot.plot(kind="bar", ax=ax, colormap="viridis")

    ax.set_title("Quarterly Posting Volume by Industry")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Number of Postings")
    ax.legend(title="Industry", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=0)

    plt.tight_layout()
    save_figure("quarterly_volume_by_industry.png", config)
    plt.show()
    logger.info("plot_quarterly_volume_by_industry complete")


def plot_yoy_growth_by_title(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Bar chart of year-over-year posting growth rate per job title
    between the first and last full year in the dataset.

    Addresses question H-04: YoY growth rate per job title.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    if not _require_temporal(df, "posted_year", "job_title"):
        return

    df_copy = df.dropna(subset=["posted_year", "job_title"]).copy()
    years = sorted(df_copy["posted_year"].dropna().astype(int).unique())

    if len(years) < 2:
        logger.warning("plot_yoy_growth_by_title: need at least 2 distinct years")
        return

    first_year, last_year = int(years[0]), int(years[-1])
    pivot = (
        df_copy.groupby(["posted_year", "job_title"])
        .size()
        .unstack(fill_value=0)
    )

    base = pivot.loc[first_year] if first_year in pivot.index else None
    current = pivot.loc[last_year] if last_year in pivot.index else None

    if base is None or current is None:
        logger.warning("plot_yoy_growth_by_title: year data incomplete")
        return

    growth = ((current - base) / base.replace(0, 1) * 100).sort_values(ascending=False)

    fig, ax = plt.subplots()
    colors = [
        get_palette(config, 2)[0] if v >= 0 else get_palette(config, 2)[1]
        for v in growth.values
    ]
    ax.bar(growth.index, growth.values, color=colors)

    ax.set_title(f"YoY Posting Growth by Job Title ({first_year} → {last_year})")
    ax.set_xlabel("Job Title")
    ax.set_ylabel("Growth Rate (%)")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    plt.xticks(rotation=30, ha="right")

    plt.tight_layout()
    save_figure("yoy_growth_by_title.png", config)
    plt.show()
    logger.info("plot_yoy_growth_by_title complete")


def plot_cumulative_postings(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Cumulative area chart of total job postings over time.

    Provides a clear visual of overall hiring acceleration across the
    full September 2023 – September 2025 observation window.

    Args:
        df: Enriched DataFrame with ``posted_year`` / ``posted_month`` columns.
        config: Loaded application configuration dictionary.
    """
    if not _require_temporal(df, "posted_year", "posted_month"):
        return

    df_copy = df.dropna(subset=["posted_year", "posted_month"]).copy()
    df_copy["year_month"] = pd.to_datetime(
        df_copy["posted_year"].astype(int).astype(str)
        + "-"
        + df_copy["posted_month"].astype(int).astype(str).str.zfill(2)
    )

    monthly = (
        df_copy.groupby("year_month")
        .size()
        .sort_index()
        .cumsum()
        .reset_index(name="cumulative")
    )

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.fill_between(
        monthly["year_month"],
        monthly["cumulative"],
        alpha=0.4,
        color=get_palette(config, 1)[0],
    )
    ax.plot(
        monthly["year_month"],
        monthly["cumulative"],
        linewidth=2,
        color=get_palette(config, 1)[0],
    )

    ax.set_title("Cumulative AI Job Postings Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Cumulative Postings")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    save_figure("cumulative_postings.png", config)
    plt.show()
    logger.info("plot_cumulative_postings complete")


def create_trend_visualizations(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Run all hiring velocity and seasonality visualizations in sequence.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    apply_style(config)
    logger.info("Generating Area 5 — Hiring Velocity and Seasonality visualizations")
    plot_monthly_posting_volume(df, config)
    plot_seasonal_pattern(df, config)
    plot_quarterly_volume_by_industry(df, config)
    plot_yoy_growth_by_title(df, config)
    plot_cumulative_postings(df, config)
    logger.info("Area 5 visualizations complete")
