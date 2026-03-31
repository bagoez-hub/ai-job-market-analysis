"""
plot_utils.py — shared visualization utilities.

All plotting modules in src/visuals/ import from here for consistent
styling, saving, and configuration handling.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

from src.utils.logger import get_logger

logger = get_logger()


# ---------------------------------------------------------------------------
# Style bootstrap
# ---------------------------------------------------------------------------


def apply_style(config: dict[str, Any]) -> None:
    """
    Apply global matplotlib / seaborn style from *config*.

    Call once at the start of each script or notebook session.

    Args:
        config: Loaded application configuration dictionary.
    """
    vis = config.get("visualization", {})
    style: str = vis.get("style", "whitegrid")
    palette: str = vis.get("palette", "viridis")
    dpi: int = vis.get("figure_dpi", 150)
    figsize: list[float] = vis.get("figure_size", [12, 5])

    sns.set_theme(style=style, palette=palette)
    plt.rcParams.update(
        {
            "figure.dpi": dpi,
            "figure.figsize": figsize,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 12,
        }
    )
    logger.debug(f"Plot style applied — style={style}, palette={palette}, dpi={dpi}")


# ---------------------------------------------------------------------------
# Figure saving
# ---------------------------------------------------------------------------


def save_figure(
    filename: str,
    config: dict[str, Any],
    dpi: int | None = None,
) -> None:
    """
    Save the current matplotlib figure to ``outputs/figures/``.

    Skips saving when running on Kaggle (``/kaggle`` root exists).

    Args:
        filename: Output file name, e.g. ``"salary_hist.png"``.
        config: Loaded application configuration dictionary.
        dpi: Override DPI (defaults to ``visualization.figure_dpi``).
    """
    if Path("/kaggle").exists():
        return

    vis = config.get("visualization", {})
    out_dir = Path(config.get("output", {}).get("figures_dir", "outputs/figures"))
    out_dir.mkdir(parents=True, exist_ok=True)

    fmt: str = vis.get("save_format", "png")
    save_dpi: int = dpi or vis.get("figure_dpi", 150)

    # Ensure the extension matches the configured format
    stem = Path(filename).stem
    dest = out_dir / f"{stem}.{fmt}"

    plt.savefig(dest, dpi=save_dpi, bbox_inches="tight")
    logger.info(f"Figure saved → {dest}")


# ---------------------------------------------------------------------------
# Axis formatters
# ---------------------------------------------------------------------------


def usd_formatter(ax: plt.Axes, axis: str = "y") -> None:
    """
    Format axis tick labels as USD integers (e.g. ``$120,000``).

    Args:
        ax: Matplotlib Axes object.
        axis: ``"x"`` or ``"y"`` (default: ``"y"``).
    """
    fmt = mticker.FuncFormatter(lambda v, _: f"${v:,.0f}")
    if axis == "y":
        ax.yaxis.set_major_formatter(fmt)
    else:
        ax.xaxis.set_major_formatter(fmt)


def percent_formatter(ax: plt.Axes, axis: str = "y") -> None:
    """
    Format axis tick labels as percentages (e.g. ``42.5%``).

    Args:
        ax: Matplotlib Axes object.
        axis: ``"x"`` or ``"y"`` (default: ``"y"``).
    """
    fmt = mticker.FuncFormatter(lambda v, _: f"{v:.1f}%")
    if axis == "y":
        ax.yaxis.set_major_formatter(fmt)
    else:
        ax.xaxis.set_major_formatter(fmt)


# ---------------------------------------------------------------------------
# Palette helper
# ---------------------------------------------------------------------------


def get_palette(config: dict[str, Any], n_colors: int = 8) -> list[str]:
    """
    Return a list of hex colours from the configured palette.

    Args:
        config: Loaded application configuration dictionary.
        n_colors: Number of colours to generate.

    Returns:
        List of hex colour strings.
    """
    palette_name: str = config.get("visualization", {}).get("palette", "viridis")
    return sns.color_palette(palette_name, n_colors=n_colors).as_hex()

