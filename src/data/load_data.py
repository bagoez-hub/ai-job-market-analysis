from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger()


def load_raw_data(config: dict[str, Any]) -> pd.DataFrame:
    """
    Load the raw AI job market CSV into a DataFrame.

    Reads the path and encoding from *config* so the function is
    fully configuration-driven and never relies on hard-coded paths.

    Args:
        config: Loaded application configuration dictionary.

    Returns:
        Raw DataFrame with all original columns intact.

    Raises:
        FileNotFoundError: When the CSV cannot be found at the configured path.
    """
    raw_path = Path(config["data"]["raw_file"])
    encoding: str = config["data"].get("encoding", "utf-8")
    delimiter: str = config["data"].get("delimiter", ",")

    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {raw_path}")

    logger.info(f"Loading raw data from {raw_path}")
    df = pd.read_csv(raw_path, encoding=encoding, sep=delimiter, low_memory=False)
    logger.info(f"Loaded {len(df):,} records, {len(df.columns)} columns")
    return df


def load_cleaned_data(config: dict[str, Any]) -> pd.DataFrame:
    """
    Load the cleaned dataset produced by the cleaning pipeline.

    Args:
        config: Loaded application configuration dictionary.

    Returns:
        Cleaned DataFrame.

    Raises:
        FileNotFoundError: When the cleaned CSV does not yet exist.
    """
    cleaned_path = Path(config["data"]["cleaned_file"])

    if not cleaned_path.exists():
        raise FileNotFoundError(
            f"Cleaned data not found at {cleaned_path}. "
            "Run the cleaning pipeline first."
        )

    logger.info(f"Loading cleaned data from {cleaned_path}")
    df = pd.read_csv(cleaned_path, low_memory=False, parse_dates=["posted_date"])
    logger.info(f"Loaded {len(df):,} records")
    return df


def load_enriched_data(config: dict[str, Any]) -> pd.DataFrame:
    """
    Load the enriched dataset produced by the enrichment pipeline.

    Args:
        config: Loaded application configuration dictionary.

    Returns:
        Enriched DataFrame.

    Raises:
        FileNotFoundError: When the enriched CSV does not yet exist.
    """
    enriched_path = Path(config["data"]["enriched_file"])

    if not enriched_path.exists():
        raise FileNotFoundError(
            f"Enriched data not found at {enriched_path}. "
            "Run the enrichment pipeline first."
        )

    logger.info(f"Loading enriched data from {enriched_path}")
    df = pd.read_csv(enriched_path, low_memory=False, parse_dates=["posted_date"])
    logger.info(f"Loaded {len(df):,} records")
    return df


def save_dataframe(
    df: pd.DataFrame,
    output_path: str | Path,
    index: bool = False,
) -> None:
    """
    Persist a DataFrame to CSV, creating parent directories as needed.

    Args:
        df: DataFrame to save.
        output_path: Destination file path.
        index: Whether to write the row index (default: False).
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    logger.info(f"Saved {len(df):,} records to {path}")

