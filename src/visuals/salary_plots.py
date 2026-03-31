"""
salary_plots.py — Area 1: Salary Trends and Benchmarks.

Covers analytical questions S-01 through S-06 from analysis-instructions.md:
  - Salary distribution (histogram + KDE)
  - Salary by experience level (box plot)
  - Salary by industry (horizontal bar)
  - Salary by job title (box plot)
  - Salary by company size (box plot)
  - Salary spread / variance by role (bar)
"""
from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from src.visuals.plot_utils import apply_style, save_figure, usd_formatter, get_palette
from src.utils.logger import get_logger

logger = get_logger()


def plot_salary_distribution(
    df: pd.DataFrame,
    config: dict[str, Any],
    column: str = "salary_avg",
) -> None:
    """
    Histogram with KDE overlay showing the overall salary distribution.

    Reveals skewness and the bulk salary band across all AI roles.

    Args:
        df: Enriched DataFrame with a numeric salary column.
        config: Loaded application configuration dictionary.
        column: Name of the salary column to plot (default: ``salary_avg``).
    """
    data = df[column].dropna()
    if data.empty:
        logger.warning(f"plot_salary_distribution: no data in column '{column}'")
        return

    fig, ax = plt.subplots()
    sns.histplot(data, bins=30, kde=True, ax=ax, color=get_palette(config, 1)[0])

    ax.set_title("Salary Distribution — All AI Roles")
    ax.set_xlabel("Salary (USD)")
    ax.set_ylabel("Number of Postings")
    usd_formatter(ax, axis="x")

    median_val = data.median()
    ax.axvline(median_val, color="crimson", linestyle="--", linewidth=1.5,
               label=f"Median: ${median_val:,.0f}")
    ax.axvline(data.mean(), color="steelblue", linestyle="--", linewidth=1.5,
               label=f"Mean: ${data.mean():,.0f}")
    ax.legend()

    plt.tight_layout()
    save_figure("salary_distribution.png", config)
    plt.show()
    logger.info("plot_salary_distribution complete")


def plot_salary_by_experience(
    df: pd.DataFrame,
    config: dict[str, Any],
    salary_col: str = "salary_avg",
) -> None:
    """
    Box plot of salary split by experience level (Entry / Mid / Senior).

    Addresses question S-01: median salary per experience tier.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        salary_col: Numeric salary column to use.
    """
    order = ["Entry", "Mid", "Senior"]
    subset = df[["experience_level", salary_col]].dropna()
    if subset.empty:
        logger.warning("plot_salary_by_experience: no data")
        return

    fig, ax = plt.subplots()
    sns.boxplot(
        data=subset,
        x="experience_level",
        y=salary_col,
        order=order,
        palette=get_palette(config, len(order)),
        ax=ax,
    )

    ax.set_title("Salary Distribution by Experience Level")
    ax.set_xlabel("Experience Level")
    ax.set_ylabel("Salary (USD)")
    usd_formatter(ax)

    plt.tight_layout()
    save_figure("salary_by_experience.png", config)
    plt.show()
    logger.info("plot_salary_by_experience complete")


def plot_salary_by_industry(
    df: pd.DataFrame,
    config: dict[str, Any],
    salary_col: str = "salary_avg",
) -> None:
    """
    Horizontal bar chart of median salary per industry, sorted descending.

    Addresses question S-02: which industries pay most / least.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        salary_col: Numeric salary column to aggregate.
    """
    subset = df[["industry", salary_col]].dropna()
    if subset.empty:
        logger.warning("plot_salary_by_industry: no data")
        return

    medians = (
        subset.groupby("industry")[salary_col]
        .median()
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots()
    colors = get_palette(config, len(medians))
    ax.barh(medians.index, medians.values, color=colors)

    ax.set_title("Median Salary by Industry")
    ax.set_xlabel("Median Salary (USD)")
    ax.set_ylabel("Industry")
    usd_formatter(ax, axis="x")

    for i, (val, label) in enumerate(zip(medians.values, medians.index)):
        ax.text(val + 500, i, f"${val:,.0f}", va="center", fontsize=9)

    plt.tight_layout()
    save_figure("salary_by_industry.png", config)
    plt.show()
    logger.info("plot_salary_by_industry complete")


def plot_salary_by_company_size(
    df: pd.DataFrame,
    config: dict[str, Any],
    salary_col: str = "salary_avg",
) -> None:
    """
    Box plot comparing salary across company sizes (Startup / Mid / Large).

    Addresses question S-03: company size effect on compensation.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        salary_col: Numeric salary column to use.
    """
    order = ["Startup", "Mid", "Large"]
    subset = df[["company_size", salary_col]].dropna()
    if subset.empty:
        logger.warning("plot_salary_by_company_size: no data")
        return

    fig, ax = plt.subplots()
    sns.boxplot(
        data=subset,
        x="company_size",
        y=salary_col,
        order=order,
        palette=get_palette(config, len(order)),
        ax=ax,
    )

    ax.set_title("Salary Distribution by Company Size")
    ax.set_xlabel("Company Size")
    ax.set_ylabel("Salary (USD)")
    usd_formatter(ax)

    plt.tight_layout()
    save_figure("salary_by_company_size.png", config)
    plt.show()
    logger.info("plot_salary_by_company_size complete")


def plot_salary_by_job_title(
    df: pd.DataFrame,
    config: dict[str, Any],
    salary_col: str = "salary_avg",
) -> None:
    """
    Horizontal box plot of salary per job title, ordered by median.

    Addresses question S-01: median salary per role.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        salary_col: Numeric salary column to use.
    """
    subset = df[["job_title", salary_col]].dropna()
    if subset.empty:
        logger.warning("plot_salary_by_job_title: no data")
        return

    order = (
        subset.groupby("job_title")[salary_col]
        .median()
        .sort_values()
        .index.tolist()
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(
        data=subset,
        y="job_title",
        x=salary_col,
        order=order,
        palette=get_palette(config, len(order)),
        ax=ax,
    )

    ax.set_title("Salary Distribution by Job Title")
    ax.set_xlabel("Salary (USD)")
    ax.set_ylabel("Job Title")
    usd_formatter(ax, axis="x")

    plt.tight_layout()
    save_figure("salary_by_job_title.png", config)
    plt.show()
    logger.info("plot_salary_by_job_title complete")


def plot_salary_variance_by_role(
    df: pd.DataFrame,
    config: dict[str, Any],
    salary_col: str = "salary_avg",
) -> None:
    """
    Bar chart of salary standard deviation per job title.

    Addresses question S-06: which roles have the greatest intra-role
    salary variance (indicating negotiation opportunity).

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        salary_col: Numeric salary column to aggregate.
    """
    subset = df[["job_title", salary_col]].dropna()
    if subset.empty:
        logger.warning("plot_salary_variance_by_role: no data")
        return

    std_vals = (
        subset.groupby("job_title")[salary_col]
        .std()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots()
    colors = get_palette(config, len(std_vals))
    ax.bar(std_vals.index, std_vals.values, color=colors)

    ax.set_title("Salary Variance (Std Dev) by Job Title")
    ax.set_xlabel("Job Title")
    ax.set_ylabel("Salary Std Dev (USD)")
    usd_formatter(ax)
    plt.xticks(rotation=30, ha="right")

    plt.tight_layout()
    save_figure("salary_variance_by_role.png", config)
    plt.show()
    logger.info("plot_salary_variance_by_role complete")


def create_salary_visualizations(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Run all salary visualizations in sequence.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    apply_style(config)
    logger.info("Generating Area 1 — Salary Trends and Benchmarks visualizations")
    plot_salary_distribution(df, config)
    plot_salary_by_experience(df, config)
    plot_salary_by_industry(df, config)
    plot_salary_by_company_size(df, config)
    plot_salary_by_job_title(df, config)
    plot_salary_variance_by_role(df, config)
    logger.info("Area 1 visualizations complete")
