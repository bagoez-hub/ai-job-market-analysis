"""
skills_plots.py — Area 2: Technical Skill and Tool Demand.

Covers analytical questions T-01 through T-06 from analysis-instructions.md:
  - Top N most frequent skills (horizontal bar)
  - Skills by experience level (grouped / diverging bar)
  - Skill salary premium (bar)
  - Tools vs skills co-occurrence (heatmap)
  - Skill demand over time (line)
  - Skill co-occurrence clusters (heatmap)
"""
from __future__ import annotations

from collections import Counter
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.visuals.plot_utils import apply_style, get_palette, save_figure, usd_formatter
from src.utils.logger import get_logger

logger = get_logger()

_SKILL_SEP = ";"  # separator used by enrich.parse_skills


def _explode_skills(series: pd.Series) -> pd.Series:
    """Split semicolon-separated skill strings into individual skill values."""
    return (
        series.dropna()
        .str.split(_SKILL_SEP)
        .explode()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
    )


def plot_top_skills(
    df: pd.DataFrame,
    config: dict[str, Any],
    column: str = "skills_required",
    top_n: int = 20,
) -> None:
    """
    Horizontal bar chart of the top *top_n* most frequently required skills.

    Addresses question T-01.

    Args:
        df: Enriched DataFrame with a normalised skills column.
        config: Loaded application configuration dictionary.
        column: Skills column to analyse (default: ``skills_required``).
        top_n: Number of top skills to display.
    """
    skills = _explode_skills(df[column])
    if skills.empty:
        logger.warning(f"plot_top_skills: no data in '{column}'")
        return

    counts = skills.value_counts().head(top_n).sort_values()

    fig, ax = plt.subplots(figsize=(10, top_n * 0.4 + 1))
    colors = get_palette(config, len(counts))
    ax.barh(counts.index, counts.values, color=colors)

    ax.set_title(f"Top {top_n} Most In-Demand Skills")
    ax.set_xlabel("Number of Postings")
    ax.set_ylabel("Skill")

    for i, val in enumerate(counts.values):
        ax.text(val + 0.3, i, str(val), va="center", fontsize=9)

    plt.tight_layout()
    save_figure("top_skills.png", config)
    plt.show()
    logger.info("plot_top_skills complete")


def plot_skills_by_experience(
    df: pd.DataFrame,
    config: dict[str, Any],
    top_n: int = 10,
) -> None:
    """
    Grouped bar chart showing top skills for each experience level side by side.

    Addresses question T-02: skills exclusive to Senior vs. Entry.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        top_n: Number of top skills to compare per level.
    """
    levels = ["Entry", "Mid", "Senior"]
    skill_counts: dict[str, pd.Series] = {}

    for level in levels:
        subset = df.loc[df["experience_level"] == level, "skills_required"]
        skills = _explode_skills(subset)
        if not skills.empty:
            skill_counts[level] = skills.value_counts().head(top_n)

    if not skill_counts:
        logger.warning("plot_skills_by_experience: no data")
        return

    combined = (
        pd.DataFrame(skill_counts)
        .fillna(0)
        .astype(int)
    )
    # Keep skills that appear in at least one level's top-N
    combined = combined[combined.sum(axis=1) > 0].sort_values("Senior", ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(12, 6))
    combined.plot(kind="bar", ax=ax, colormap="viridis")

    ax.set_title(f"Top {top_n} Skills by Experience Level")
    ax.set_xlabel("Skill")
    ax.set_ylabel("Number of Postings")
    ax.legend(title="Experience Level")
    plt.xticks(rotation=35, ha="right")

    plt.tight_layout()
    save_figure("skills_by_experience.png", config)
    plt.show()
    logger.info("plot_skills_by_experience complete")


def plot_skill_salary_premium(
    df: pd.DataFrame,
    config: dict[str, Any],
    salary_col: str = "salary_avg",
    top_n: int = 15,
) -> None:
    """
    Bar chart of average salary premium for postings that list each skill.

    Addresses question T-03: which skills command the highest salary.

    Args:
        df: Enriched DataFrame with ``salary_avg`` and ``skills_required``.
        config: Loaded application configuration dictionary.
        salary_col: Numeric salary column to use.
        top_n: Number of skills to display.
    """
    rows = df[["skills_required", salary_col]].dropna()
    if rows.empty:
        logger.warning("plot_skill_salary_premium: no data")
        return

    # Expand each row into (skill, salary) pairs
    records: list[dict] = []
    for _, row in rows.iterrows():
        for skill in str(row["skills_required"]).split(_SKILL_SEP):
            skill = skill.strip()
            if skill:
                records.append({"skill": skill, salary_col: row[salary_col]})

    expanded = pd.DataFrame(records)
    skill_salary = (
        expanded.groupby("skill")[salary_col]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(10, top_n * 0.45 + 1))
    colors = get_palette(config, len(skill_salary))
    ax.barh(skill_salary.index, skill_salary.values, color=colors)

    ax.set_title(f"Top {top_n} Skills by Average Salary Premium")
    ax.set_xlabel("Average Salary (USD)")
    ax.set_ylabel("Skill")
    usd_formatter(ax, axis="x")

    plt.tight_layout()
    save_figure("skill_salary_premium.png", config)
    plt.show()
    logger.info("plot_skill_salary_premium complete")


def plot_skill_demand_over_time(
    df: pd.DataFrame,
    config: dict[str, Any],
    top_n: int = 8,
) -> None:
    """
    Line chart showing quarterly posting volume for the top *top_n* skills.

    Addresses question T-05: how skill demand has shifted over time.

    Args:
        df: Enriched DataFrame with ``posted_date`` or ``posted_quarter`` /
            ``posted_year`` columns and ``skills_required``.
        config: Loaded application configuration dictionary.
        top_n: Number of skills to track.
    """
    needed = {"skills_required", "posted_year", "posted_quarter"}
    if not needed.issubset(df.columns):
        logger.warning(
            "plot_skill_demand_over_time: missing required columns — "
            f"need {needed - set(df.columns)}"
        )
        return

    # Find global top skills
    top_skills = (
        _explode_skills(df["skills_required"])
        .value_counts()
        .head(top_n)
        .index.tolist()
    )

    records: list[dict] = []
    for _, row in df.dropna(subset=["skills_required", "posted_year"]).iterrows():
        period = f"Q{int(row['posted_quarter'])} {int(row['posted_year'])}"
        for skill in str(row["skills_required"]).split(_SKILL_SEP):
            skill = skill.strip()
            if skill in top_skills:
                records.append({"period": period, "skill": skill})

    if not records:
        logger.warning("plot_skill_demand_over_time: no matching data")
        return

    pivot = (
        pd.DataFrame(records)
        .groupby(["period", "skill"])
        .size()
        .unstack(fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(14, 5))
    pivot.plot(ax=ax, marker="o", colormap="viridis")

    ax.set_title(f"Quarterly Demand for Top {top_n} Skills")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Number of Postings")
    ax.legend(title="Skill", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    save_figure("skill_demand_over_time.png", config)
    plt.show()
    logger.info("plot_skill_demand_over_time complete")


def plot_skill_cooccurrence(
    df: pd.DataFrame,
    config: dict[str, Any],
    top_n: int = 12,
) -> None:
    """
    Heatmap of skill co-occurrence frequency among the top *top_n* skills.

    Addresses question T-06: skill clusters / stack signatures.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
        top_n: Number of top skills to include in the co-occurrence matrix.
    """
    skills_series = _explode_skills(df["skills_required"])
    top_skills = skills_series.value_counts().head(top_n).index.tolist()

    matrix = pd.DataFrame(0, index=top_skills, columns=top_skills)

    for raw in df["skills_required"].dropna():
        posting_skills = [
            s.strip() for s in str(raw).split(_SKILL_SEP) if s.strip() in top_skills
        ]
        for i, s1 in enumerate(posting_skills):
            for s2 in posting_skills[i + 1:]:
                matrix.loc[s1, s2] += 1
                matrix.loc[s2, s1] += 1

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        matrix,
        cmap="viridis",
        linewidths=0.5,
        annot=True,
        fmt="d",
        ax=ax,
    )
    ax.set_title(f"Skill Co-occurrence — Top {top_n} Skills")

    plt.tight_layout()
    save_figure("skill_cooccurrence.png", config)
    plt.show()
    logger.info("plot_skill_cooccurrence complete")


def create_skills_visualizations(
    df: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    """
    Run all skill and tool demand visualizations in sequence.

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.
    """
    apply_style(config)
    logger.info("Generating Area 2 — Technical Skill and Tool Demand visualizations")
    plot_top_skills(df, config)
    plot_skills_by_experience(df, config)
    plot_skill_salary_premium(df, config)
    plot_skill_demand_over_time(df, config)
    plot_skill_cooccurrence(df, config)
    logger.info("Area 2 visualizations complete")
