"""
geo_industry_plots.py — Area 4: Geographic and Industry Demand.

Covers analytical questions G-01 through G-05 from analysis-instructions.md:
  - Top hiring cities (horizontal bar)
  - Salary distribution by location (box plot)
  - Industry dominance per city (stacked bar)
  - Role concentration by location (heatmap)
  - Industry AI hiring share over time (line)
"""
from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.visuals.plot_utils import apply_style, get_palette, save_figure, usd_formatter
from src.utils.logger import get_logger

logger = get_logger()


def plot_top_hiring_cities(
    df: pd.DataFrame,
    config: dict[str, Any],
    top_n: int = 10,
) -> None:
    """
    Horizontal bar chart of cities with the highest posting concentration.

    Addresses question G-01.

    Args:
        df: Enriched DataFrame with a ``location`` column.
        config: Loaded application configuration dictionary.
        top_n: Number of cities to display.
    """
    cities = df["location"].dropna()
    if cities.empty:
        logger.warning("plot_top_hiring_cities: no location data")
        return

    counts = cities.value_counts().head(top_n).sort_values()

    fig, ax = plt.subplots(figsize=(10, top_n * 0.45 + 1))
    colors = get_palette(config, len(counts))
    ax.barh(counts.index, counts.values, color=colors)
    ax.set_title(f"Top {top_n} Hiring Cities")
    ax.set_xlabel("Number of Postings")
    ax.set_ylabel("Location")

    for i, val in enumerate(counts.values):
        ax.text(val + 0.2, i, str(val), va="center", fontsize=9)

    plt.tight_layout()
    save_figure("top_hiring_cities.png", config)
    plt.show()
    logger.info("plot_top_hiring_cities complete")


def plot_salary_by_location(
    df: pd.DataFrame,
    config: dict[str, Any],
    salary_col: str = "salary_avg",
    top_n: int = 10,
) -> None:
    """
    Horizontal box plot of salary distribution for the top *top_n* locations.

    Addresses question G-02: salary distribution per geographic region.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        salary_col: Numeric salary column to use.
        top_n: Number of top locations (by posting count) to include.
    """
    top_locs = df["location"].value_counts().head(top_n).index
    subset = df[df["location"].isin(top_locs)][["location", salary_col]].dropna()

    if subset.empty:
        logger.warning("plot_salary_by_location: no data")
        return

    order = (
        subset.groupby("location")[salary_col]
        .median()
        .sort_values()
        .index.tolist()
    )

    fig, ax = plt.subplots(figsize=(10, top_n * 0.5 + 1))
    sns.boxplot(
        data=subset,
        y="location",
        x=salary_col,
        order=order,
        palette=get_palette(config, len(order)),
        ax=ax,
    )
    ax.set_title(f"Salary by Location — Top {top_n} Cities")
    ax.set_xlabel("Salary (USD)")
    ax.set_ylabel("Location")
    usd_formatter(ax, axis="x")

    plt.tight_layout()
    save_figure("salary_by_location.png", config)
    plt.show()
    logger.info("plot_salary_by_location complete")


def plot_industry_by_city(
    df: pd.DataFrame,
    config: dict[str, Any],
    top_n_cities: int = 8,
) -> None:
    """
    Stacked bar chart showing industry composition within the top cities.

    Addresses question G-03: which industries dominate each geographic cluster.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        top_n_cities: Number of top cities to include.
    """
    top_cities = df["location"].value_counts().head(top_n_cities).index
    subset = df[df["location"].isin(top_cities)]

    pivot = (
        subset.groupby(["location", "industry"])
        .size()
        .unstack(fill_value=0)
        .reindex(top_cities)
    )
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(12, 5))
    pivot_pct.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")

    ax.set_title(f"Industry Composition in Top {top_n_cities} Cities")
    ax.set_xlabel("City")
    ax.set_ylabel("Share of Postings (%)")
    ax.legend(title="Industry", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")

    plt.tight_layout()
    save_figure("industry_by_city.png", config)
    plt.show()
    logger.info("plot_industry_by_city complete")


def plot_role_concentration_heatmap(
    df: pd.DataFrame,
    config: dict[str, Any],
    top_n_cities: int = 10,
) -> None:
    """
    Heatmap of job title frequency across the top cities.

    Addresses question G-04: roles uniquely concentrated in certain locations.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        top_n_cities: Number of top cities (by posting count) to include.
    """
    top_cities = df["location"].value_counts().head(top_n_cities).index
    subset = df[df["location"].isin(top_cities)]

    pivot = (
        subset.groupby(["location", "job_title"])
        .size()
        .unstack(fill_value=0)
        .reindex(top_cities)
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(
        pivot,
        cmap="viridis",
        annot=True,
        fmt="d",
        linewidths=0.4,
        ax=ax,
    )
    ax.set_title(f"Job Title Concentration — Top {top_n_cities} Cities")
    ax.set_xlabel("Job Title")
    ax.set_ylabel("City")
    plt.xticks(rotation=30, ha="right")

    plt.tight_layout()
    save_figure("role_concentration_heatmap.png", config)
    plt.show()
    logger.info("plot_role_concentration_heatmap complete")


def plot_industry_hiring_share_over_time(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Line chart of each industry's share of total AI hiring per quarter.

    Addresses question G-05: industries with rising vs. declining AI hiring share.

    Args:
        df: Enriched DataFrame with ``posted_year`` and ``posted_quarter``.
        config: Loaded application configuration dictionary.
    """
    needed = {"industry", "posted_year", "posted_quarter"}
    if not needed.issubset(df.columns):
        logger.warning(
            "plot_industry_hiring_share_over_time: missing columns — "
            f"{needed - set(df.columns)}"
        )
        return

    df_copy = df.dropna(subset=["industry", "posted_year", "posted_quarter"]).copy()
    df_copy["period"] = (
        "Q" + df_copy["posted_quarter"].astype(int).astype(str)
        + " " + df_copy["posted_year"].astype(int).astype(str)
    )

    pivot = (
        df_copy.groupby(["period", "industry"])
        .size()
        .unstack(fill_value=0)
    )
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(14, 5))
    pivot_pct.plot(ax=ax, marker="o", colormap="viridis")

    ax.set_title("Industry Share of AI Hiring — Quarterly Trend")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Share of Total Postings (%)")
    ax.legend(title="Industry", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    save_figure("industry_hiring_share_trend.png", config)
    plt.show()
    logger.info("plot_industry_hiring_share_over_time complete")


def create_geo_industry_visualizations(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Run all geographic and industry demand visualizations in sequence.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    apply_style(config)
    logger.info("Generating Area 4 — Geographic and Industry Demand visualizations")
    plot_top_hiring_cities(df, config)
    plot_salary_by_location(df, config)
    plot_industry_by_city(df, config)
    plot_role_concentration_heatmap(df, config)
    plot_industry_hiring_share_over_time(df, config)
    logger.info("Area 4 visualizations complete")
