"""
forecasting_analysis.py — Hiring velocity and seasonality analysis.

Covers analysis area A5: Hiring Velocity and Seasonality.
  - Monthly posting volume time series
  - Seasonal patterns (month-of-year aggregation)
  - Year-over-year growth rates
  - Short-term job count forecast via Exponential Smoothing or ARIMA
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger()


# ---------------------------------------------------------------------------
# Time series preparation
# ---------------------------------------------------------------------------


def prepare_time_series(
    df: pd.DataFrame,
    date_col: str = "posted_date",
    value_col: str = "job_count",
    frequency: str = "ME",
) -> pd.Series:
    """
    Aggregate postings into a regular monthly time series.

    Since the raw dataset contains one row per posting (not aggregated),
    *value_col* is always computed as the **count of rows** per period.

    Args:
        df: Enriched DataFrame with a datetime *date_col*.
        date_col: Name of the datetime column to resample over.
        value_col: Ignored — present for API compatibility; always counts rows.
        frequency: Pandas offset alias for resampling (default: ``"ME"`` = month-end).

    Returns:
        Monthly Series of posting counts indexed by period-end dates,
        with NaN periods filled to zero.
    """
    if date_col not in df.columns:
        logger.warning(f"prepare_time_series: '{date_col}' not found — returning empty Series")
        return pd.Series(dtype=float)

    ts = (
        df.set_index(date_col)
        .resample(frequency)
        .size()
        .rename("job_count")
        .astype(float)
    )
    # Fill gaps so the series is continuous
    ts = ts.fillna(0)
    logger.debug(
        f"prepare_time_series: {len(ts)} monthly periods, "
        f"total postings = {int(ts.sum())}"
    )
    return ts


def seasonal_pattern(ts: pd.Series) -> pd.DataFrame:
    """
    Compute average posting count by calendar month (seasonal profile).

    Args:
        ts: Monthly time series from :func:`prepare_time_series`.

    Returns:
        DataFrame with columns [month, avg_postings, month_name].
    """
    if ts.empty:
        return pd.DataFrame()
    monthly_avg = ts.groupby(ts.index.month).mean().reset_index()
    monthly_avg.columns = ["month", "avg_postings"]
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
    }
    monthly_avg["month_name"] = monthly_avg["month"].map(month_names)
    return monthly_avg


def yoy_growth(ts: pd.Series) -> pd.DataFrame:
    """
    Compute year-over-year (YoY) growth in monthly posting volume.

    Args:
        ts: Monthly time series from :func:`prepare_time_series`.

    Returns:
        DataFrame with columns [year, month, job_count, yoy_growth_pct].
    """
    if ts.empty:
        return pd.DataFrame()
    df_ts = ts.reset_index()
    df_ts.columns = ["date", "job_count"]
    df_ts["year"] = df_ts["date"].dt.year
    df_ts["month"] = df_ts["date"].dt.month

    yoy = df_ts.merge(
        df_ts[["year", "month", "job_count"]].rename(
            columns={"year": "prev_year", "job_count": "prev_count"}
        ).assign(year=lambda x: x["prev_year"] + 1),
        on=["year", "month"],
        how="left",
    )
    yoy["yoy_growth_pct"] = (
        (yoy["job_count"] - yoy["prev_count"]) / yoy["prev_count"].replace(0, pd.NA) * 100
    ).round(2)
    return yoy[["date", "year", "month", "job_count", "yoy_growth_pct"]].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Forecasting
# ---------------------------------------------------------------------------


def forecast_jobs(
    ts: pd.Series,
    horizon: int = 6,
    model: Literal["exponential_smoothing", "arima"] = "exponential_smoothing",
) -> pd.DataFrame:
    """
    Forecast future monthly job posting counts.

    Supported models:
    - ``"exponential_smoothing"``: Holt-Winters additive seasonality via
      ``statsmodels.tsa.holtwinters.ExponentialSmoothing``.
    - ``"arima"``: Auto-regressive ARIMA(1,1,1) via
      ``statsmodels.tsa.arima.model.ARIMA``.

    Args:
        ts: Monthly time series produced by :func:`prepare_time_series`.
            Must have at least 24 observations for seasonal smoothing.
        horizon: Number of months ahead to forecast (default: 6).
        model: Forecasting model to use (default: ``"exponential_smoothing"``).

    Returns:
        DataFrame with columns [date, forecast] for the forecast horizon,
        followed by the historical series for comparison.
    """
    if ts.empty or len(ts) < 4:
        logger.warning("forecast_jobs: insufficient data for forecasting")
        return pd.DataFrame(columns=["date", "forecast"])

    try:
        if model == "exponential_smoothing":
            from statsmodels.tsa.holtwinters import ExponentialSmoothing

            # Use additive seasonality only when enough data (≥24 months)
            use_seasonal = len(ts) >= 24
            fit = ExponentialSmoothing(
                ts,
                trend="add",
                seasonal="add" if use_seasonal else None,
                seasonal_periods=12 if use_seasonal else None,
            ).fit(optimized=True)
            forecast_values = fit.forecast(horizon)

        elif model == "arima":
            from statsmodels.tsa.arima.model import ARIMA

            fit = ARIMA(ts, order=(1, 1, 1)).fit()
            forecast_values = fit.forecast(steps=horizon)

        else:
            logger.error(f"forecast_jobs: unknown model '{model}'")
            return pd.DataFrame(columns=["date", "forecast"])

    except Exception as exc:
        logger.error(f"forecast_jobs: model fitting failed — {exc}")
        return pd.DataFrame(columns=["date", "forecast"])

    # Build forecast DataFrame
    last_date = ts.index[-1]
    forecast_index = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=horizon,
        freq="ME",
    )
    forecast_df = pd.DataFrame(
        {"date": forecast_index, "forecast": forecast_values.clip(lower=0).values}
    )
    logger.info(
        f"forecast_jobs: {model} forecast for {horizon} months, "
        f"mean predicted = {forecast_values.mean():.1f} postings/month"
    )
    return forecast_df


# ---------------------------------------------------------------------------
# Full forecasting orchestration
# ---------------------------------------------------------------------------


def run_forecasting(df: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    """
    Execute the complete hiring velocity and seasonality analysis (Area A5).

    Steps:
    1. Build monthly posting time series
    2. Compute seasonal pattern (avg by calendar month)
    3. Compute YoY growth rates
    4. Forecast the next *horizon* months using the configured model

    Args:
        df: Enriched DataFrame.
        config: Loaded application configuration dictionary.

    Returns:
        Dictionary with keys:
        - ``"monthly_ts"`` — raw monthly Series
        - ``"seasonal_pattern"`` — DataFrame of monthly averages
        - ``"yoy_growth"`` — DataFrame with YoY growth percentages
        - ``"forecast"`` — DataFrame of future posting count predictions
        - ``"config_used"`` — forecasting config snapshot
    """
    fc_cfg = config.get("analysis", {}).get("forecasting", {})
    enabled: bool = fc_cfg.get("enabled", True)
    date_col: str = fc_cfg.get("time_column", "posted_date")
    horizon: int = fc_cfg.get("horizon", 6)
    freq: str = fc_cfg.get("frequency", "ME")
    model_name: str = fc_cfg.get("model", "exponential_smoothing")

    # Normalise pandas freq alias
    if freq == "M":
        freq = "ME"

    logger.info(f"Running forecasting analysis — model={model_name}, horizon={horizon} months")

    ts = prepare_time_series(df, date_col=date_col, frequency=freq)
    seasonal = seasonal_pattern(ts)
    growth = yoy_growth(ts)
    forecast_df = forecast_jobs(ts, horizon=horizon, model=model_name) if enabled else pd.DataFrame()

    tables_dir = Path(config.get("output", {}).get("tables_dir", "outputs/tables"))
    tables_dir.mkdir(parents=True, exist_ok=True)

    # Save time series and outputs
    ts_df = ts.reset_index()
    ts_df.columns = ["date", "job_count"]
    ts_df.to_csv(tables_dir / "forecast_monthly_ts.csv", index=False)

    if not seasonal.empty:
        seasonal.to_csv(tables_dir / "forecast_seasonal_pattern.csv", index=False)
    if not growth.empty:
        growth.to_csv(tables_dir / "forecast_yoy_growth.csv", index=False)
    if not forecast_df.empty:
        forecast_df.to_csv(tables_dir / "forecast_predictions.csv", index=False)
        logger.info(f"Forecast saved → {tables_dir / 'forecast_predictions.csv'}")

    logger.info("Forecasting analysis complete")
    return {
        "monthly_ts": ts,
        "seasonal_pattern": seasonal,
        "yoy_growth": growth,
        "forecast": forecast_df,
        "config_used": fc_cfg,
    }
