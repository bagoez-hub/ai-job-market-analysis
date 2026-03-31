"""
employment_plots.py — Area 3: Employment Dynamics and Company Profiles.

Covers analytical questions E-01 through E-05 from analysis-instructions.md:
  - Employment type share (pie / donut)
  - Remote-friendly job titles (horizontal bar)
  - Experience level mix by company size (stacked bar)
  - Employment type share by industry (stacked bar)
  - Posting volume by company size and experience (heatmap)
"""
from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.visuals.plot_utils import apply_style, get_palette, save_figure
from src.utils.logger import get_logger

logger = get_logger()


def plot_employment_type_share(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Donut chart showing the share of postings by employment type.

    Addresses question E-01: Full-time vs. Remote vs. Contract vs. Internship.

    Args:
        df: Enriched DataFrame with ``employment_type`` column.
        config: Loaded application configuration dictionary.
    """
    counts = df["employment_type"].value_counts()
    if counts.empty:
        logger.warning("plot_employment_type_share: no data")
        return

    colors = get_palette(config, len(counts))
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        wedgeprops={"width": 0.55},  # donut style
    )
    for at in autotexts:
        at.set_fontsize(10)

    ax.set_title("Employment Type Share")
    plt.tight_layout()
    save_figure("employment_type_share.png", config)
    plt.show()
    logger.info("plot_employment_type_share complete")


def plot_remote_roles(
    df: pd.DataFrame,
    config: dict[str, Any],
    top_n: int = 10,
) -> None:
    """
    Horizontal bar chart of job titles most frequently offered as Remote.

    Addresses question E-02.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        top_n: Number of top titles to display.
    """
    remote = df[df["employment_type"] == "Remote"]
    if remote.empty:
        logger.warning("plot_remote_roles: no Remote postings found")
        return

    counts = remote["job_title"].value_counts().head(top_n).sort_values()

    fig, ax = plt.subplots()
    colors = get_palette(config, len(counts))
    ax.barh(counts.index, counts.values, color=colors)
    ax.set_title(f"Top {top_n} Job Titles Offered as Remote")
    ax.set_xlabel("Number of Postings")
    ax.set_ylabel("Job Title")

    for i, val in enumerate(counts.values):
        ax.text(val + 0.1, i, str(val), va="center", fontsize=9)

    plt.tight_layout()
    save_figure("remote_roles.png", config)
    plt.show()
    logger.info("plot_remote_roles complete")


def plot_experience_mix_by_company_size(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Stacked bar chart of experience level mix broken down by company size.

    Addresses question E-03: how experience mix differs between Startups
    and Large companies.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    size_order = ["Startup", "Mid", "Large"]
    exp_order = ["Entry", "Mid", "Senior"]

    pivot = (
        df.groupby(["company_size", "experience_level"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=size_order, columns=exp_order, fill_value=0)
    )
    # Normalise to percentages
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots()
    pivot_pct.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        colormap="viridis",
    )
    ax.set_title("Experience Level Mix by Company Size")
    ax.set_xlabel("Company Size")
    ax.set_ylabel("Share of Postings (%)")
    ax.legend(title="Experience Level", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=0)

    plt.tight_layout()
    save_figure("experience_mix_by_company_size.png", config)
    plt.show()
    logger.info("plot_experience_mix_by_company_size complete")


def plot_employment_type_by_industry(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Stacked bar chart of employment type distribution per industry.

    Addresses question E-04: which industries show the highest proportion
    of Contract or Internship roles.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    pivot = (
        df.groupby(["industry", "employment_type"])
        .size()
        .unstack(fill_value=0)
    )
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(12, 5))
    pivot_pct.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")

    ax.set_title("Employment Type Distribution by Industry")
    ax.set_xlabel("Industry")
    ax.set_ylabel("Share of Postings (%)")
    ax.legend(title="Employment Type", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")

    plt.tight_layout()
    save_figure("employment_type_by_industry.png", config)
    plt.show()
    logger.info("plot_employment_type_by_industry complete")


def plot_posting_heatmap_size_experience(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Heatmap of posting count by company size × experience level.

    Addresses question E-05: which company sizes generate the most
    entry-level postings.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    size_order = ["Startup", "Mid", "Large"]
    exp_order = ["Entry", "Mid", "Senior"]

    pivot = (
        df.groupby(["company_size", "experience_level"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=size_order, columns=exp_order, fill_value=0)
    )

    fig, ax = plt.subplots()
    sns.heatmap(
        pivot,
        cmap="viridis",
        annot=True,
        fmt="d",
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title("Posting Count — Company Size × Experience Level")
    ax.set_xlabel("Experience Level")
    ax.set_ylabel("Company Size")

    plt.tight_layout()
    save_figure("posting_heatmap_size_experience.png", config)
    plt.show()
    logger.info("plot_posting_heatmap_size_experience complete")


def create_employment_visualizations(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Run all employment dynamics and company profile visualizations.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    apply_style(config)
    logger.info("Generating Area 3 — Employment Dynamics and Company Profiles visualizations")
    plot_employment_type_share(df, config)
    plot_remote_roles(df, config)
    plot_experience_mix_by_company_size(df, config)
    plot_employment_type_by_industry(df, config)
    plot_posting_heatmap_size_experience(df, config)
    logger.info("Area 3 visualizations complete")
