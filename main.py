"""
main.py — AI Job Market Analysis Pipeline

Orchestrates the full ETL and analysis workflow:
  1. Bootstrap logger and load configuration
  2. Load raw data → validate schema → clean → quality-check → enrich → save
  3. Run EDA          (src/analysis/exploratory.py)
  4. Run KPI analysis (src/analysis/kpi_analysis.py)
  5. Run segmentation (src/analysis/segmentation_analysis.py)
  6. Run forecasting  (src/analysis/forecasting_analysis.py)
  7. Generate visualizations for all five thematic areas
  8. Export enriched dataset to CSV and Parquet
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from src.utils.logger import get_logger, setup_logger
from src.utils.helpers import load_config, LogExecutionTime

from src.data.load_data import load_raw_data, save_dataframe
from src.data.clean_data import clean_pipeline
from src.data.validate import validate_raw_data, check_data_quality
from src.data.enrich import enrich_pipeline

from src.analysis.exploratory import run_eda
from src.analysis.kpi_analysis import calculate_kpis
from src.analysis.segmentation_analysis import analyze_segments
from src.analysis.forecasting_analysis import run_forecasting

from src.visuals.plot_utils import apply_style
from src.visuals.salary_plots import create_salary_visualizations
from src.visuals.skills_plots import create_skills_visualizations
from src.visuals.employment_plots import create_employment_visualizations
from src.visuals.geo_industry_plots import create_geo_industry_visualizations
from src.visuals.trend_plots import create_trend_visualizations


def main(config_path: str = "config/config.yaml") -> None:
    """
    Execute the end-to-end AI job market analysis pipeline.

    Args:
        config_path: Path to the YAML configuration file.
    """
    # -----------------------------------------------------------------------
    # 1. Logger and configuration
    # -----------------------------------------------------------------------
    setup_logger(log_level="INFO")
    logger = get_logger()

    logger.info("=" * 60)
    logger.info("AI Job Market Analysis Pipeline — starting")
    logger.info("=" * 60)

    config: dict[str, Any] = load_config(config_path)
    logger.info(
        f"Config loaded — project: {config['project']['name']}, "
        f"version: {config['version']}"
    )

    # -----------------------------------------------------------------------
    # 2. Data pipeline: Load → Validate → Clean → Quality-check → Enrich → Save
    # -----------------------------------------------------------------------
    with LogExecutionTime("Data pipeline (load → enrich)"):

        # Load
        raw_df = load_raw_data(config)

        # Schema validation (Pydantic row-by-row)
        try:
            _, validation_report = validate_raw_data(raw_df, config)
            logger.info(
                f"Schema validation passed — "
                f"{validation_report['total_rows']:,} rows, "
                f"{validation_report['duplicate_job_ids']} duplicate job_ids"
            )
        except (ValueError, AssertionError) as exc:
            logger.error(f"Schema validation failed: {exc}")
            sys.exit(1)

        # Cleaning
        cleaned_df = clean_pipeline(raw_df, config)

        # Post-cleaning quality gate
        quality_report = check_data_quality(cleaned_df, config)
        if not quality_report["passed"]:
            logger.warning(
                f"Data quality check did not fully pass — "
                f"completeness: {quality_report['overall_completeness']:.2%}, "
                f"duplicate ratio: {quality_report['duplicate_ratio']:.2%}. "
                f"Continuing pipeline."
            )

        # Save cleaned data
        cleaned_path = Path(config["data"]["cleaned_file"])
        save_dataframe(cleaned_df, cleaned_path)

        # Enrichment
        enriched_df = enrich_pipeline(cleaned_df, config)

        # Save enriched data
        enriched_path = Path(config["data"]["enriched_file"])
        save_dataframe(enriched_df, enriched_path)

    # -----------------------------------------------------------------------
    # 3. EDA — exploratory analysis
    # -----------------------------------------------------------------------
    with LogExecutionTime("EDA"):
        eda_report = run_eda(enriched_df, config)
        logger.info(
            f"EDA complete — "
            f"salary median: ${eda_report['salary_distribution'].get('median', 'N/A'):,}, "
            f"monthly data points: {len(eda_report['monthly_posting_trend'])}"
        )

    # -----------------------------------------------------------------------
    # 4. KPI analysis — A1 Salary Benchmarks + A3 Employment Dynamics
    # -----------------------------------------------------------------------
    with LogExecutionTime("KPI analysis"):
        kpis = calculate_kpis(enriched_df, config)
        overall_salary = kpis["salary_overall"]
        logger.info(
            f"KPI analysis complete — "
            f"mean salary: ${overall_salary.get('mean', 0):,.0f}, "
            f"median salary: ${overall_salary.get('median', 0):,.0f}"
        )

    # -----------------------------------------------------------------------
    # 5. Segmentation analysis — A2 Skills/Tools + A3 Employment + A4 Geo/Industry
    # -----------------------------------------------------------------------
    with LogExecutionTime("Segmentation analysis"):
        segments = analyze_segments(enriched_df, config)
        top_skill = (
            segments["top_skills"].iloc[0]["skill"]
            if not segments["top_skills"].empty
            else "N/A"
        )
        top_city = (
            segments["top_hiring_locations"].iloc[0]["location"]
            if not segments["top_hiring_locations"].empty
            else "N/A"
        )
        logger.info(
            f"Segmentation complete — "
            f"top skill: {top_skill}, "
            f"top hiring city: {top_city}"
        )

    # -----------------------------------------------------------------------
    # 6. Forecasting — A5 Hiring Velocity and Seasonality
    # -----------------------------------------------------------------------
    with LogExecutionTime("Forecasting analysis"):
        forecast_results = run_forecasting(enriched_df, config)
        forecast_df = forecast_results["forecast"]
        if not forecast_df.empty:
            avg_forecast = forecast_df["forecast"].mean()
            logger.info(
                f"Forecasting complete — "
                f"avg predicted postings/month over next "
                f"{len(forecast_df)} months: {avg_forecast:.1f}"
            )
        else:
            logger.info("Forecasting complete — no forecast generated (disabled or insufficient data)")

    # -----------------------------------------------------------------------
    # 7. Visualizations
    # -----------------------------------------------------------------------
    with LogExecutionTime("Visualizations"):
        apply_style(config)

        # A1 — Salary trends
        logger.info("Generating A1 — Salary Trends and Benchmarks visualizations")
        create_salary_visualizations(enriched_df, config)

        # A2 — Skills and tools
        logger.info("Generating A2 — Technical Skill and Tool Demand visualizations")
        create_skills_visualizations(enriched_df, config)

        # A3 — Employment dynamics
        logger.info("Generating A3 — Employment Dynamics and Company Profiles visualizations")
        create_employment_visualizations(enriched_df, config)

        # A4 — Geographic and industry
        logger.info("Generating A4 — Geographic and Industry Demand visualizations")
        create_geo_industry_visualizations(enriched_df, config)

        # A5 — Hiring velocity and seasonality
        logger.info("Generating A5 — Hiring Velocity and Seasonality visualizations")
        create_trend_visualizations(enriched_df, config)

    # -----------------------------------------------------------------------
    # 8. Exports
    # -----------------------------------------------------------------------
    with LogExecutionTime("Exports"):
        exports_dir = Path(config.get("output", {}).get("exports_dir", "outputs/exports"))
        exports_dir.mkdir(parents=True, exist_ok=True)

        for export_cfg in config.get("output", {}).get("exports", []):
            fmt: str = export_cfg.get("format", "csv")
            out_path = Path(export_cfg.get("path", f"outputs/exports/ai_jobs_summary.{fmt}"))
            out_path.parent.mkdir(parents=True, exist_ok=True)

            if fmt == "csv":
                enriched_df.to_csv(out_path, index=False)
                logger.info(f"Exported CSV → {out_path}")
            elif fmt == "parquet":
                compression: str = export_cfg.get("compression", "snappy")
                enriched_df.to_parquet(out_path, index=False, compression=compression)
                logger.info(f"Exported Parquet ({compression}) → {out_path}")
            else:
                logger.warning(f"Unknown export format '{fmt}' — skipped")

    # -----------------------------------------------------------------------
    # Done
    # -----------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("Pipeline completed successfully")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
