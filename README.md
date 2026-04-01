# AI Job Market Analysis

A data analysis pipeline for the AI/ML job market, covering 2,000 job postings from September 2023 to September 2025. Built around reliable, reproducible, and maintainable data principles — idempotent pipelines, Pydantic validation, configuration-driven logic, and structured logging.

---

## Table of Contents

1. [Dataset](#1-dataset)
2. [Analysis Areas](#2-analysis-areas)
3. [Project Structure](#3-project-structure)
4. [Tech Stack](#4-tech-stack)
5. [Getting Started](#5-getting-started)
6. [Running the Pipeline](#6-running-the-pipeline)
7. [Outputs](#7-outputs)
8. [Key Insights Produced](#8-key-insights-produced)
9. [Users of This Analysis](#9-users-of-this-analysis)
10. [Development](#10-development)

---

## 1. Dataset

| Property | Detail |
|---|---|
| **File** | `data/raw/ai_job_market.csv` |
| **Records** | 2,000 job postings |
| **Date Range** | September 2023 — September 2025 |
| **Granularity** | One row = one job posting |

### Schema

| Column | Type | Description |
|---|---|---|
| `job_id` | int | Unique posting identifier |
| `company_name` | str | Hiring company |
| `industry` | str | Automotive, E-commerce, Education, Finance, Healthcare, Retail, Tech |
| `job_title` | str | AI Product Manager, AI Researcher, Computer Vision Engineer, Data Analyst, Data Scientist, ML Engineer, NLP Engineer, Quant Researcher |
| `skills_required` | str (comma-sep) | Core technical skills listed in the posting |
| `tools_preferred` | str (comma-sep) | Secondary / preferred tooling |
| `experience_level` | str | Entry, Mid, Senior |
| `employment_type` | str | Full-time, Contract, Remote, Internship |
| `location` | str | City and country/state code |
| `salary_range_usd` | str | Range in format `min-max` (USD) |
| `posted_date` | date | ISO 8601 posting date |
| `company_size` | str | Startup, Mid, Large |

> **Note**: `data/raw/` is excluded from version control. Source the dataset externally and place `ai_job_market.csv` in `data/raw/` before running the pipeline.

---

## 2. Analysis Areas

The project is organized into five thematic areas, each mapping to one or more source modules under `src/analysis/`.

### Area 1 — Salary Trends and Benchmarks
Compensation patterns across roles, seniority levels, industries, and company sizes. Identify salary bands and flag anomalies.
**Modules**: `kpi_analysis.py`, `exploratory.py`

### Area 2 — Technical Skill and Tool Demand
Decompose `skills_required` and `tools_preferred` to reveal in-demand technologies, co-occurrence clusters, and demand shifts over time.
**Modules**: `exploratory.py`, `segmentation_analysis.py`

### Area 3 — Employment Dynamics and Company Profiles
Profile hiring landscape by employment type, experience level, and company size. Identify structural patterns in how different company archetypes hire.
**Modules**: `segmentation_analysis.py`, `kpi_analysis.py`

### Area 4 — Geographic and Industry Demand
Map job concentration by location and industry. Identify high-demand hubs and cross-reference geography with salary and seniority.
**Modules**: `exploratory.py`, `segmentation_analysis.py`

### Area 5 — Hiring Velocity and Seasonality
Use `posted_date` to build time-series views of posting volume. Detect seasonal cycles and acceleration/deceleration trends.
**Modules**: `forecasting_analysis.py`

### Area 6 — Salary Prediction and ML Modeling
Build regression models to predict salary from role, experience, industry, company size, and skill features. Evaluate feature importance and quantify the marginal contribution of each variable to compensation.
**Modules**: `kpi_analysis.py`, `segmentation_analysis.py`
**Notebook**: `notebooks/03_analysis/07_salary_prediction.ipynb`

---

## 3. Project Structure

```
ai_job_market/
├── config/
│   ├── config.yaml             # Main pipeline configuration
│   ├── logging.yaml            # Loguru logging configuration
│   └── paths.yaml              # Data path definitions
├── data/
│   ├── raw/                    # Source data (not tracked — see §1)
│   ├── cleaned/                # Cleaned & validated data (pipeline output)
│   ├── enriched/               # Feature-engineered data (pipeline output)
│   ├── external/               # External reference datasets
│   └── dictionary/             # Data dictionaries and schemas
├── notebooks/
│   ├── 01_exploration/         # Exploratory data analysis
│   ├── 02_cleaning/            # Data cleaning walkthroughs
│   ├── 03_analysis/            # Statistical analysis
│   └── 04_visuals/             # Visualization notebooks
├── outputs/
│   ├── figures/                # Generated plots (not tracked — regenerate via pipeline)
│   ├── tables/                 # Summary CSV tables
│   └── exports/                # Exported datasets (CSV, Parquet)
├── reports/                    # Markdown analysis reports
├── src/
│   ├── data/
│   │   ├── load_data.py        # Data loading functions
│   │   ├── clean_data.py       # Cleaning pipeline (pure functions)
│   │   ├── enrich.py           # Feature engineering
│   │   └── validate.py         # Schema & quality validation
│   ├── analysis/
│   │   ├── exploratory.py      # EDA — summary stats, distributions
│   │   ├── kpi_analysis.py     # KPI calculations (salary benchmarks)
│   │   ├── segmentation_analysis.py  # Segmentation by category
│   │   └── forecasting_analysis.py   # Time-series forecasting
│   ├── visuals/
│   │   ├── plot_utils.py       # Shared plotting utilities
│   │   ├── salary_plots.py     # Salary visualization suite
│   │   ├── skills_plots.py     # Skills demand charts
│   │   ├── employment_plots.py # Employment type & experience charts
│   │   ├── geo_industry_plots.py # Geographic & industry heatmaps
│   │   └── trend_plots.py      # Hiring velocity & seasonality plots
│   └── utils/
│       ├── helpers.py          # Config loader, composition utilities
│       └── logger.py           # Loguru setup
├── main.py                     # Pipeline entry point
└── pyproject.toml              # Project metadata & tool config
```

### Pipeline Execution Order

```
Stage 0 — Data Preparation
    load_data.py → clean_data.py → validate.py → enrich.py

Stage 1 — Foundational EDA  (all EDA checkpoints must pass)
    exploratory.py

Stage 2 — Parallel Analysis  (run concurrently after Stage 1)
    ├── kpi_analysis.py           (Areas 1 & 3)
    ├── segmentation_analysis.py  (Areas 2, 3 & 4)
    ├── forecasting_analysis.py   (Area 5)
    └── salary prediction model   (Area 6 — notebook 07)
```

---

## 4. Tech Stack

| Category | Libraries |
|---|---|
| **Language** | Python 3.14+ |
| **Data Processing** | pandas, numpy, scipy |
| **Validation** | Pydantic v2, pydantic-settings |
| **Machine Learning** | scikit-learn, statsmodels |
| **Visualization** | matplotlib, seaborn, plotly |
| **Logging** | loguru |
| **Configuration** | PyYAML |
| **Notebooks** | Jupyter, ipykernel |
| **Export** | pyarrow (Parquet) |
| **Testing** | pytest, pytest-cov |
| **Code Quality** | ruff, black, mypy |

---

## 5. Getting Started

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd ai_job_market

# Create and activate virtual environment with uv
uv venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
uv sync

# Install dev dependencies
uv sync --group dev
```

### Dataset Setup

Place the raw dataset in the expected location:

```
data/raw/ai_job_market.csv
```

### Environment Variables

Copy and configure the environment file:

```bash
copy .env.example .env    # Windows
# cp .env.example .env   # macOS/Linux
```

---

## 6. Running the Pipeline

### Full Pipeline

```bash
python main.py
```

This executes all stages — data loading, cleaning, validation, enrichment, EDA, KPI analysis, segmentation, forecasting, and visualization generation.

### Individual Stages

```python
from src.utils.helpers import load_config
from src.data.load_data import load_raw_data
from src.data.clean_data import clean_pipeline
from src.data.validate import validate_raw_data, check_data_quality
from src.data.enrich import enrich_pipeline

config = load_config("config/config.yaml")
raw_df = load_raw_data(config)
cleaned_df = clean_pipeline(raw_df, config)
_, report = validate_raw_data(cleaned_df, config)
enriched_df = enrich_pipeline(cleaned_df, config)
```

### Notebooks

```bash
jupyter notebook notebooks/01_exploration/
```

Notebooks are organized by analysis stage and follow the numbered prefix convention (`01_`, `02_`, etc.).

---

## 7. Outputs

| Output | Location | Description |
|---|---|---|
| Cleaned dataset | `data/cleaned/ai_job_market_cleaned.csv` | Deduplicated, typed, null-handled |
| Enriched dataset | `data/enriched/ai_job_market_enriched.csv` | + salary features, temporal features, skill dummies |
| Summary export | `outputs/exports/ai_jobs_summary.csv` | Aggregated insights export |
| KPI tables | `outputs/tables/kpi_*.csv` | Salary benchmarks by dimension |
| Segmentation tables | `outputs/tables/seg_*.csv` | Cross-tabulations by segment |
| Forecast tables | `outputs/tables/forecast_*.csv` | Time-series predictions |
| EDA tables | `outputs/tables/eda_*.csv` | Distribution and stats summaries |
| Figures | `outputs/figures/*.png` | 300 dpi charts (regenerated each run) |
| Reports | `reports/` | Dated Markdown analysis reports |

### Output Naming Conventions

| Prefix | Area |
|---|---|
| `kpi_` | Salary & KPI benchmarks |
| `seg_` | Segmentation analysis |
| `forecast_` | Hiring velocity & forecasting |
| `eda_` | Exploratory data analysis |

---

## 8. Key Insights Produced

### Salary Trends & Benchmarks
- Median and mean compensation per role and seniority tier
- Salary premium of Senior over Entry level ($ and %)
- Company size effect on pay (Startup vs. Mid vs. Large)
- Industries with the widest salary spread

### Technical Skill & Tool Demand
- Top 20 most frequently required skills across all postings
- Skills that appear exclusively in Senior vs. Entry-level roles
- Skills commanding the highest salary premium
- Skill co-occurrence clusters by job title

### Employment Dynamics
- Share of postings by employment type (Full-time, Remote, Contract, Internship)
- Roles most commonly offered as Remote or Contract
- Experience level distribution across company sizes

### Geographic & Industry Demand
- Top 10 hiring cities and their role concentrations
- Industries with rising vs. declining AI hiring share
- Cross-tabulation of industry × role for niche demand pockets

### Hiring Velocity & Seasonality
- Month-over-month and year-over-year posting volume trends
- Consistent seasonal patterns (peak months, summer slowdowns)
- Industry-level seasonality differences
- Time-series forecast for the next two quarters

### Salary Prediction & ML Modeling
- Regression model predicting salary from role, experience, industry, company size, and skills
- Feature importance ranking — which variables drive compensation the most
- Marginal salary premium attributable to each seniority tier
- Model performance benchmarks (MAE, RMSE, R²) and residual analysis

---

## 9. Users of This Analysis

| User | Primary Interest | Expected Output |
|---|---|---|
| **Job Seekers** | Salary benchmarks, skill demand, geographic hotspots | Salary negotiation reference, skill prioritization guide |
| **Hiring Managers** | Competitive salary ranges, skill landscape, seasonality | Compensation benchmarks, talent availability windows |
| **Recruiters** | Hiring velocity, employment dynamics, geographic demand | Pipeline timing strategy, sourcing targets |
| **L&D / Training Teams** | Skill demand, experience level gaps | Curriculum prioritization, upskilling roadmaps |
| **Investors / Analysts** | Industry demand, hiring velocity, company profiles | AI sector growth signals, industry heat maps |

---

## 10. Development

### Code Quality

```bash
# Format
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

### Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=html
```

### Core Principles

| Principle | Implementation |
|---|---|
| **Idempotency** | Pure functions; same input always produces same output |
| **Data Quality Gates** | Pydantic validation at load; quality checks post-clean and post-enrich |
| **Configuration-Driven** | All behavior controlled via `config/config.yaml` — no hardcoded values |
| **Functional Style** | DataFrames copied before every transformation; originals never mutated |
| **Reproducibility** | Fixed random seed (`42`); deterministic sort order throughout |
| **Observable** | Structured loguru logging with record counts at every pipeline stage |

### Configuration

The main configuration file is `config/config.yaml`. It controls:

- Data file paths and encoding
- Processing behaviour (deduplication, missing-value strategy, outlier detection)
- Feature engineering flags (salary extraction, temporal features, skill dummies)
- Analysis parameters (segmentation groups, forecasting horizon and model)
- Visualization style (palette, DPI, figure dimensions)
- Output paths and export formats

---

*Last Updated: 2026-04-01 | Dataset: `ai_job_market.csv` (2,000 records, Sep 2023 – Sep 2025)*
