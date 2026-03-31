# AI Job Market — Analysis Instructions

> **Purpose**: This document is the canonical roadmap for the AI job market analysis project. It defines what we are investigating, the insights we expect to extract, who will use them, and the quality checkpoints every analyst must follow before publishing results.

---

## Table of Contents

1. [Dataset Overview](#1-dataset-overview)
2. [Analysis Areas](#2-analysis-areas)
3. [Insights That Can Be Gained](#3-insights-that-can-be-gained)
4. [Analytical Questions](#4-analytical-questions)
5. [Users of This Analysis](#5-users-of-this-analysis)
6. [EDA Checkpoints](#6-eda-checkpoints)
7. [Analysis Execution Order](#7-analysis-execution-order)
8. [Output Standards](#8-output-standards)

---

## 1. Dataset Overview

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

---

## 2. Analysis Areas

The analysis is organized into **five thematic areas**. Each area maps to one or more source modules under `src/analysis/`.

### Area 1 — Salary Trends and Benchmarks

Understand compensation patterns across roles, seniority levels, industries, and company sizes. Identify meaningful salary bands and flag anomalies.

**Source modules**: `kpi_analysis.py`, `exploratory.py`

---

### Area 2 — Technical Skill and Tool Demand

Decompose the `skills_required` and `tools_preferred` columns to reveal which technologies employers actively demand, how co-occurrence clusters form, and how demand has shifted over the observation window.

**Source modules**: `exploratory.py`, `segmentation_analysis.py`

---

### Area 3 — Employment Dynamics and Company Profiles

Profile the hiring landscape by employment type (Full-time, Contract, Remote, Internship), experience level, and company size. Identify structural patterns in how different company archetypes hire.

**Source modules**: `segmentation_analysis.py`, `kpi_analysis.py`

---

### Area 4 — Geographic and Industry Demand

Map job concentration by location and industry. Identify high-demand hubs and underserved markets. Cross-reference geography with salary and seniority to surface regional disparities.

**Source modules**: `exploratory.py`, `segmentation_analysis.py`

---

### Area 5 — Hiring Velocity and Seasonality

Use `posted_date` to build time-series views of posting volume. Detect seasonal cycles, acceleration or deceleration trends, and industry-specific hiring windows.

**Source modules**: `forecasting_analysis.py`

---

## 3. Insights That Can Be Gained

### Salary Trends and Benchmarks
- Median and mean compensation per role and seniority tier
- Salary premium of Senior over Entry level ($ and %)
- Industries with the widest salary spread (high variance)
- Company size effect on pay — do Startups or Large companies pay more for the same role?
- Outlier postings with unusually high or low ranges

### Technical Skill and Tool Demand
- Top N skills by raw posting frequency
- Fastest-growing skills (quarter-over-quarter change)
- Skills that consistently co-occur (skill bundles / stack signatures)
- Skill gaps — roles with low median salary that still demand advanced tools
- Differentiation between "required" skills vs. "preferred" tools by role type

### Employment Dynamics and Company Profiles
- Share of postings by employment type (Full-time vs. Remote vs. Contract vs. Internship)
- Experience level distribution across company sizes
- Roles most commonly offered as Remote or Contract
- Which company sizes generate the largest share of entry-level postings

### Geographic and Industry Demand
- Top 10 hiring cities and their role concentrations
- Industries with rising vs. declining AI hiring share
- Salary-adjusted demand index by location (high pay + high volume = hotspot)
- Cross-tab of industry × role to find niche pockets of demand

### Hiring Velocity and Seasonality
- Monthly and quarterly posting volume trends
- Year-over-year growth rate across the full dataset
- Seasonal peaks (e.g., Q1 hiring surges, summer slowdowns)
- Industry-level seasonality differences
- Leading indicators for future demand spikes

---

## 4. Analytical Questions

### Area 1 — Salary Trends and Benchmarks

| # | Question | Priority |
|---|---|---|
| S-01 | What is the median salary for each job title, broken down by experience level? | High |
| S-02 | Which industries offer the highest and lowest average salaries for the same role? | High |
| S-03 | How does company size (Startup vs. Mid vs. Large) correlate with salary range width and midpoint? | High |
| S-04 | What percentage of postings omit or provide incomplete salary data? | Medium |
| S-05 | Are there statistically significant salary differences between employment types (Full-time vs. Contract)? | Medium |
| S-06 | Which roles have the greatest intra-role salary variance — indicating negotiation opportunity? | Low |

### Area 2 — Technical Skill and Tool Demand

| # | Question | Priority |
|---|---|---|
| T-01 | What are the top 20 most frequently required skills across all postings? | High |
| T-02 | Which skills appear exclusively in Senior-level vs. Entry-level postings? | High |
| T-03 | What skills command the highest salary premium when listed? | High |
| T-04 | Which tools are most often listed as "preferred" alongside which required skills? | Medium |
| T-05 | How has the demand for specific skills (e.g., LangChain, CUDA) changed year-over-year? | Medium |
| T-06 | What skill clusters (co-occurrence groups) define each job title's canonical stack? | Low |

### Area 3 — Employment Dynamics and Company Profiles

| # | Question | Priority |
|---|---|---|
| E-01 | What is the share of Full-time vs. Remote vs. Contract vs. Internship postings? | High |
| E-02 | Which job titles are most frequently offered as Remote? | High |
| E-03 | How does the experience level mix differ between Startups and Large companies? | High |
| E-04 | Which industries show the highest proportion of Contract or Internship roles? | Medium |
| E-05 | Do companies with more postings (high-volume hirers) skew toward specific experience levels? | Low |

### Area 4 — Geographic and Industry Demand

| # | Question | Priority |
|---|---|---|
| G-01 | Which cities have the highest concentration of AI job postings? | High |
| G-02 | What is the salary distribution per geographic region after cost-of-living normalization? | High |
| G-03 | Which industries dominate AI hiring in each geographic cluster? | Medium |
| G-04 | Are there locations where certain roles are uniquely concentrated vs. distributed nationally? | Medium |
| G-05 | Which industries have increased their AI hiring share over the observation period? | Low |

### Area 5 — Hiring Velocity and Seasonality

| # | Question | Priority |
|---|---|---|
| H-01 | What is the month-over-month posting volume trend for the full dataset? | High |
| H-02 | Is there a consistent seasonal pattern (peak months) in AI hiring? | High |
| H-03 | Which industries post the most roles in Q1 vs. Q3? | Medium |
| H-04 | What is the year-over-year growth rate in total postings per job title? | Medium |
| H-05 | Can a simple time-series model forecast posting volume for the next two quarters? | Low |

---

## 5. Users of This Analysis

| User | Role | Primary Areas of Interest | Expected Output |
|---|---|---|---|
| **Job Seekers** | Individuals targeting AI roles | Salary benchmarks (S), Skill demand (T), Geographic hotspots (G) | Salary negotiation reference, skill prioritization guide |
| **Hiring Managers** | Leads defining job requirements | Competitive salary ranges (S), Skill landscape (T), Seasonality (H) | Compensation benchmarks, talent availability windows |
| **Recruiters** | Talent acquisition teams | Hiring velocity (H), Employment dynamics (E), Geographic demand (G) | Pipeline timing strategy, location sourcing targets |
| **L&D / Training Teams** | Learning and development professionals | Technical skill demand (T), Experience level gaps (E) | Curriculum prioritization, upskilling roadmaps |
| **Investors / Analysts** | Market researchers, VCs | Industry demand (G), Hiring velocity (H), Company profiles (E) | AI sector growth signals, industry heat maps |
| **Data Science Team** | Internal analysts building this pipeline | All areas | Reproducible pipeline, validated outputs, documented findings |

---

## 6. EDA Checkpoints

All five areas share a common set of EDA checkpoints that **must be completed and documented** before any analysis module is finalized. Use the [EDA Checkpoint Template](#eda-checkpoint-template) below for reporting.

### Checkpoint 1 — Schema Validation
- [ ] All expected columns present and correctly named
- [ ] Column data types match schema definition (especially `posted_date` as date, `salary_range_usd` as str)
- [ ] No extra or unexpected columns introduced during loading

### Checkpoint 2 — Completeness Assessment
- [ ] Missing value count and percentage reported per column
- [ ] Rows with >50% null fields flagged for review
- [ ] `salary_range_usd` completeness confirmed (this column is critical to Areas 1 and 3)
- [ ] `skills_required` and `tools_preferred` null rate assessed

### Checkpoint 3 — Uniqueness and Duplicates
- [ ] `job_id` confirmed unique — zero duplicates
- [ ] Near-duplicate detection run on (`company_name`, `job_title`, `posted_date`, `location`) composite key
- [ ] Duplicate records removed before downstream analysis

### Checkpoint 4 — Distribution Profiling
- [ ] Frequency table generated for all categorical columns (`industry`, `job_title`, `experience_level`, `employment_type`, `company_size`)
- [ ] Salary midpoint distribution plotted (after parsing `salary_range_usd`)
- [ ] `posted_date` distribution plotted as monthly posting volume
- [ ] Skewness and kurtosis reported for salary midpoint

### Checkpoint 5 — Salary Parsing and Validation
- [ ] `salary_range_usd` successfully split into `salary_min` and `salary_max` integer columns
- [ ] Records where `salary_min > salary_max` flagged and investigated
- [ ] Salary midpoint (`(salary_min + salary_max) / 2`) derived and stored
- [ ] Values outside plausible range (`< $10,000` or `> $1,500,000`) identified and reviewed

### Checkpoint 6 — Skills Tokenization
- [ ] `skills_required` and `tools_preferred` exploded into one-skill-per-row format for frequency analysis
- [ ] Skill label normalization applied (strip whitespace, title-case, deduplicate synonyms)
- [ ] Skill vocabulary size reported (number of unique skills)

### Checkpoint 7 — Temporal Integrity
- [ ] `posted_date` confirmed parseable with no ambiguous formats
- [ ] Date range validated — no future dates beyond dataset end, no implausible historical dates
- [ ] Monthly time index constructed as a continuous series (fill zero for months with no postings)

### Checkpoint 8 — Outlier Flagging
- [ ] IQR-based outlier detection applied to salary midpoint per role
- [ ] Extreme posting volume months identified (> 3σ from mean)
- [ ] Outlier records tagged with a flag column — **not deleted** — for analyst review

### Checkpoint 9 — Cross-Column Consistency
- [ ] `experience_level` × `salary_min` correlation checked for monotonicity (Entry < Mid < Senior expected)
- [ ] `employment_type = "Internship"` rows confirmed to have `experience_level = "Entry"` or flagged
- [ ] `company_size` distribution validated within each `industry`

### Checkpoint 10 — Baseline Summary Statistics
- [ ] Summary statistics table exported to `outputs/tables/eda_summary_stats.csv`
- [ ] Null rate heatmap saved to `outputs/figures/eda_null_heatmap.png`
- [ ] Posting volume time-series plot saved to `outputs/figures/eda_posting_volume.png`
- [ ] All findings logged via `loguru` at `INFO` level with record counts

---

### EDA Checkpoint Template

Use this block in your notebook cell or script comment to record checkpoint status:

```
EDA Checkpoint Summary
======================
Area          : <Area name>
Analyst       : <Name>
Date          : <YYYY-MM-DD>
Dataset Shape : <rows> × <cols>

Checkpoint Results
------------------
1. Schema Validation     : PASS / FAIL / PARTIAL — <notes>
2. Completeness          : PASS / FAIL / PARTIAL — <notes>
3. Uniqueness            : PASS / FAIL / PARTIAL — <notes>
4. Distribution Profiling: PASS / FAIL / PARTIAL — <notes>
5. Salary Parsing        : PASS / FAIL / PARTIAL — <notes>
6. Skills Tokenization   : PASS / FAIL / PARTIAL — <notes>
7. Temporal Integrity    : PASS / FAIL / PARTIAL — <notes>
8. Outlier Flagging      : PASS / FAIL / PARTIAL — <notes>
9. Cross-Column Consistency: PASS / FAIL / PARTIAL — <notes>
10. Baseline Stats        : PASS / FAIL / PARTIAL — <notes>

Blockers / Open Items
---------------------
- <List any issues that block downstream analysis>
```

---

## 7. Analysis Execution Order

Run areas in this sequence to ensure upstream outputs are available to downstream modules.

```
Stage 0 — Data Preparation
    load_data.py  →  clean_data.py  →  validate.py  →  enrich.py

Stage 1 — Foundational EDA  (all EDA Checkpoints must pass)
    exploratory.py

Stage 2 — Parallel Analysis  (can run concurrently after Stage 1)
    ├── kpi_analysis.py          (Areas 1 & 3)
    ├── segmentation_analysis.py (Areas 2, 3 & 4)
    └── forecasting_analysis.py  (Area 5)

Stage 3 — Reporting
    plot_utils.py  →  outputs/figures/  +  outputs/tables/  →  reports/
```

---

## 8. Output Standards

| Output Type | Location | Naming Convention | Format |
|---|---|---|---|
| Cleaned data | `data/cleaned/` | `jobs_cleaned.parquet` | Parquet |
| Enriched data | `data/enriched/` | `jobs_enriched.parquet` | Parquet |
| Summary tables | `outputs/tables/` | `<area>_<metric>.csv` | CSV |
| Figures | `outputs/figures/` | `<area>_<chart_type>.png` | PNG (300 dpi) |
| Exports | `outputs/exports/` | `<area>_results.json` | JSON |
| Reports | `reports/` | `<YYYY-MM-DD>_<topic>_report.md` | Markdown |

### Figure Standards
- Figure size: `(12, 6)` for wide charts, `(8, 8)` for square/matrix charts
- DPI: `300` for all saved figures
- Color palette: `viridis` for continuous, `Set2` for categorical
- Every figure must have a title, labeled axes, and a data source annotation

### Reproducibility Requirements
- Random seed: `42` for all stochastic operations
- All intermediate DataFrames written to `data/enriched/` before use in Stage 2
- Pipeline must produce identical outputs on repeated runs (idempotent)
- All steps logged with `loguru` including record counts before and after each transformation

---

*Last Updated: 2026-03-31 | Dataset: `ai_job_market.csv` (2,000 records, Sep 2023 – Sep 2025)*
