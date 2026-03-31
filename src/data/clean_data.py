from __future__ import annotations

from typing import Any, Literal

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger()


# ---------------------------------------------------------------------------
# Individual pure-function cleaning steps
# ---------------------------------------------------------------------------


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lowercase and strip all column names.

    Args:
        df: Input DataFrame.

    Returns:
        New DataFrame with normalised column names.
    """
    result = df.copy()
    result.columns = [c.strip().lower() for c in result.columns]
    return result


def remove_duplicates(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    """
    Drop exact duplicate rows, optionally keyed on *subset* columns.

    Args:
        df: Input DataFrame.
        subset: Column(s) used to identify duplicates. When *None* all columns
            are used.

    Returns:
        Deduplicated copy of the DataFrame.
    """
    before = len(df)
    result = df.drop_duplicates(subset=subset).reset_index(drop=True)
    removed = before - len(result)
    if removed:
        logger.debug(f"remove_duplicates: dropped {removed:,} duplicate row(s)")
    return result


def handle_missing_values(
    df: pd.DataFrame,
    strategy: Literal["default", "drop", "impute"] = "default",
    impute_method: Literal["median", "mean", "mode"] = "median",
    threshold: float = 0.5,
) -> pd.DataFrame:
    """
    Handle missing values according to the chosen strategy.

    Strategies:
    - ``"default"``: Fill numeric columns with their median; leave text
      columns with *NaN* so downstream code can flag them explicitly.
    - ``"drop"``: Drop rows that have *any* null in required columns.
    - ``"impute"``: Fill numeric NaNs with the specified *impute_method*.

    Columns whose null ratio exceeds *threshold* are dropped regardless
    of strategy (matches config ``processing.handle_missing.threshold``).

    Args:
        df: Input DataFrame.
        strategy: Missing-value handling strategy.
        impute_method: Aggregation used for numeric imputation.
        threshold: Maximum allowed null ratio before a column is dropped.

    Returns:
        Cleaned copy of the DataFrame.
    """
    result = df.copy()

    # Drop columns that are mostly empty
    null_ratios = result.isnull().mean()
    drop_cols = null_ratios[null_ratios > threshold].index.tolist()
    if drop_cols:
        result = result.drop(columns=drop_cols)
        logger.debug(f"handle_missing_values: dropped high-null columns {drop_cols}")

    numeric_cols = result.select_dtypes(include="number").columns

    if strategy in ("default", "impute"):
        for col in numeric_cols:
            if result[col].isnull().any():
                filler: float
                if impute_method == "mean":
                    filler = float(result[col].mean())
                elif impute_method == "mode":
                    mode_vals = result[col].mode()
                    filler = float(mode_vals.iloc[0]) if not mode_vals.empty else 0.0
                else:
                    filler = float(result[col].median())
                result[col] = result[col].fillna(filler)

    elif strategy == "drop":
        before = len(result)
        result = result.dropna().reset_index(drop=True)
        logger.debug(
            f"handle_missing_values: dropped {before - len(result):,} row(s) "
            f"with null values"
        )

    return result


def standardize_text_fields(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    Strip leading/trailing whitespace and normalise internal spacing for
    string columns.

    Args:
        df: Input DataFrame.
        columns: Explicit list of columns to standardise. When *None*, all
            object-typed columns are processed.

    Returns:
        DataFrame with cleaned string columns.
    """
    result = df.copy()
    target_cols = columns if columns is not None else result.select_dtypes("object").columns.tolist()
    for col in target_cols:
        if col in result.columns:
            result[col] = result[col].str.strip().str.replace(r"\s+", " ", regex=True)
    return result


def parse_dates(df: pd.DataFrame, date_columns: list[str]) -> pd.DataFrame:
    """
    Parse string date columns to ``datetime64[ns]``.

    Args:
        df: Input DataFrame.
        date_columns: Names of columns to convert.

    Returns:
        DataFrame with date columns as proper datetimes.
    """
    result = df.copy()
    for col in date_columns:
        if col in result.columns:
            result[col] = pd.to_datetime(result[col], errors="coerce")
            nat_count = result[col].isna().sum()
            if nat_count:
                logger.warning(
                    f"parse_dates: {nat_count:,} unparseable value(s) in '{col}' → NaT"
                )
    return result


def remove_outliers_iqr(
    df: pd.DataFrame,
    columns: list[str],
    factor: float = 3.0,
) -> pd.DataFrame:
    """
    Remove rows where numeric values fall beyond *factor* × IQR from Q1/Q3.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to check.
        factor: IQR multiplier for the fence (default: 3.0 from config).

    Returns:
        DataFrame with outlier rows removed.
    """
    result = df.copy()
    for col in columns:
        if col not in result.columns:
            continue
        q1 = result[col].quantile(0.25)
        q3 = result[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        before = len(result)
        result = result[result[col].between(lower, upper)].reset_index(drop=True)
        removed = before - len(result)
        if removed:
            logger.debug(
                f"remove_outliers_iqr: removed {removed:,} outlier(s) in '{col}' "
                f"[{lower:,.0f}, {upper:,.0f}]"
            )
    return result


# ---------------------------------------------------------------------------
# Orchestrated cleaning pipeline
# ---------------------------------------------------------------------------


def clean_pipeline(raw_df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """
    Run the full cleaning pipeline according to *config*.

    Steps (all idempotent):
    1. Standardise column names
    2. Parse date columns
    3. Standardise text fields
    4. Remove duplicate job_ids
    5. Handle missing values
    6. Remove outliers on numeric columns (if enabled)

    Args:
        raw_df: Raw DataFrame from :func:`~src.data.load_data.load_raw_data`.
        config: Loaded application configuration dictionary.

    Returns:
        Cleaned DataFrame — original *raw_df* is never modified.
    """
    proc = config.get("processing", {})
    data_cfg = config.get("data", {})

    df = standardize_column_names(raw_df)

    # Date parsing
    date_cols: list[str] = data_cfg.get("date_columns", ["posted_date"])
    df = parse_dates(df, date_cols)

    # Text normalisation
    df = standardize_text_fields(df)

    # Deduplication
    dedup_cfg = proc.get("remove_duplicates", {})
    if dedup_cfg.get("enabled", True):
        subset: list[str] = dedup_cfg.get("subset", ["job_id"])
        df = remove_duplicates(df, subset=subset)

    # Missing values
    missing_cfg = proc.get("handle_missing", {})
    df = handle_missing_values(
        df,
        strategy=missing_cfg.get("strategy", "default"),
        impute_method=missing_cfg.get("impute_method", "median"),
        threshold=missing_cfg.get("threshold", 0.5),
    )

    # Outlier removal (only on numeric columns that exist after enrichment)
    outlier_cfg = proc.get("outlier_detection", {})
    if outlier_cfg.get("enabled", True):
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            df = remove_outliers_iqr(
                df,
                columns=numeric_cols,
                factor=outlier_cfg.get("threshold", 3.0),
            )

    logger.info(
        f"clean_pipeline complete — {len(raw_df):,} → {len(df):,} rows, "
        f"{len(df.columns)} columns"
    )
    return df

