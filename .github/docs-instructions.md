# Documentation Writing Guide

## Overview

This guide defines how to write two types of project documentation:

1. **Markdown Reports** (`.md`) — Human-readable analysis summaries with statistical explanations and chart insights.
2. **Jupyter Notebooks** (`.ipynb`) — Compiled, self-contained, reproducible reports published to Kaggle.

---

## Part 1: Markdown Report Writing Guide

Markdown reports document the **findings** from processed data. They are written for technical and semi-technical audiences who want to understand *what the numbers mean*, not just see them.

### 1.1 Document Structure

Every markdown report must follow this structure:

```
# Report Title

## 1. Overview
## 2. Dataset Summary
## 3. Statistical Analysis
## 4. Visualizations & Chart Insights
## 5. Key Findings
## 6. Recommendations
```

### 1.2 Statistical Analysis Section

Explain each statistical method used — do not assume the reader already knows what it means.

#### Descriptive Statistics

| Statistic | What It Measures | When to Use It |
|-----------|-----------------|----------------|
| **Mean** | Arithmetic average of all values | Continuous, normally distributed data (e.g., average salary) |
| **Median** | Middle value when sorted | Skewed data or when outliers are present (e.g., median salary by location) |
| **Mode** | Most frequently occurring value | Categorical or discrete data (e.g., most common job title) |
| **Standard Deviation** | Spread / variability around the mean | Measuring how consistent data is |
| **Variance** | Square of standard deviation | Quantifying overall dispersion |
| **Percentiles (P25, P75, IQR)** | Distribution range excluding extremes | Identifying outliers or salary bands |

**Writing Rule**: Always state the statistic value, what it implies, and why it matters.

```markdown
### Salary Distribution

The **mean salary** across all AI roles is **$112,450**, while the **median** sits at **$98,200**.
The gap between mean and median (~$14K) indicates a **right-skewed distribution** — a smaller
number of high-paying senior roles pull the average upward. For most job seekers, the median is
a more realistic salary benchmark.

The **interquartile range (IQR)** spans from **$78,000 (P25)** to **$142,000 (P75)**,
meaning 50% of AI jobs fall within this salary band.
```

#### Correlation Analysis

- Use **Pearson correlation** for linear relationships between continuous variables (e.g., experience level vs. salary).
- Use **Spearman correlation** for monotonic or non-normal relationships.
- Always include a correlation heatmap and interpret the strongest relationships.

```markdown
### Correlation Insights

Experience level shows a **strong positive correlation (r = 0.72)** with salary, confirming
that seniority is the primary salary driver in AI roles. Notably, company size has only a
**moderate correlation (r = 0.38)**, suggesting large companies do not always pay the highest.
```

#### Regression Analysis

- State whether it is **Linear**, **Polynomial**, **Logistic**, or another type.
- Report the **R² score** and interpret it (proportion of variance explained).
- Report **coefficients** and their effect direction (positive/negative).
- Mention **p-values** and statistical significance where applicable.

```markdown
### Salary Regression Model

A **multiple linear regression** model was trained to predict salary from job features.

**Model Performance**: R² = 0.81 (the model explains 81% of salary variance)

**Key Predictors**:
- `experience_level` (Senior → +$42,000 vs Entry-level)
- `industry` (Tech → +$18,500 vs Healthcare)
- `company_size` (Large → +$9,200 vs Small)

The model indicates that **experience level is the strongest salary predictor** by a significant
margin, followed by industry sector.
```

#### Segmentation / Grouping Analysis

When grouping data (by location, industry, job type), always:

1. State the **grouping criterion**.
2. Report the **aggregate metric** (mean, count, percentage).
3. Highlight the **top and bottom groups** and explain possible causes.

```markdown
### Salary by Industry

| Industry | Median Salary | Count |
|----------|--------------|-------|
| Tech | $128,400 | 3,210 |
| Finance | $115,800 | 1,870 |
| Healthcare | $94,200 | 1,340 |
| Education | $71,500 | 620 |

Tech and Finance command significantly higher salaries, likely due to **higher product margins**
and **greater competition for AI talent** in these sectors.
```

#### Distribution & Outlier Analysis

- Use **histograms** or **box plots** to show distribution shape.
- Flag outliers explicitly and state whether they were removed or retained.
- Explain the effect of outliers on downstream analysis.

```markdown
### Outlier Detection

Salaries above **$350,000** (> 3 standard deviations from mean) were identified as outliers
(n = 47 records, 0.3% of dataset). These likely represent **C-suite or founding team roles**
rather than standard market positions. They were **excluded from regression modeling** to avoid
skewing coefficients, but retained in the full distribution visualizations.
```

---

### 1.3 Visualizations & Chart Insights Section

Each chart must be documented with:
1. **Chart Type** and the library used (`matplotlib`, `seaborn`, `plotly`)
2. **What the chart shows** (axes, groupings, encodings)
3. **How to read it**
4. **The key insight or takeaway**

#### Histogram

```markdown
#### Salary Distribution Histogram
*Library: seaborn | Type: Histogram with KDE*

**Chart**: X-axis = salary (USD), Y-axis = frequency count. Overlaid KDE curve shows
the density estimate of the distribution.

**How to Read**: Bars represent the count of jobs in each salary bin ($10K wide).
The KDE curve smooths the distribution shape.

**Insight**: The distribution is **right-skewed** with a long tail above $200K.
The bulk of AI jobs (68%) cluster between $70,000 and $150,000.
```

#### Box Plot

```markdown
#### Salary by Experience Level — Box Plot
*Library: seaborn | Type: Box Plot*

**Chart**: X-axis = experience level (Entry / Mid / Senior), Y-axis = salary (USD).
Each box represents Q1–Q3 range, line = median, whiskers = 1.5×IQR, dots = outliers.

**How to Read**: A taller box means more salary variability within that group.
Dots above the whiskers are statistical outliers.

**Insight**: Senior roles have the **widest salary spread** (IQR: $85K–$195K), suggesting
greater variance in senior compensation compared to Entry-level roles (IQR: $55K–$90K).
```

#### Heatmap

```markdown
#### Correlation Heatmap
*Library: seaborn | Type: Heatmap*

**Chart**: Rows and columns = numeric features. Cell color = Pearson correlation coefficient
(-1 = dark red, 0 = white, +1 = dark blue).

**How to Read**: Strong colors (deep red or blue) indicate strong correlations.
Values close to 0 indicate little relationship.

**Insight**: `experience_level` and `salary` show the strongest correlation (r = 0.72).
`posted_date` shows near-zero correlation with salary (r = 0.03), confirming salary is
not significantly influenced by when a job was posted.
```

#### Bar Chart

```markdown
#### Top 10 Most In-Demand Skills — Horizontal Bar Chart
*Library: matplotlib | Type: Horizontal Bar Chart*

**Chart**: Y-axis = skill name, X-axis = number of job postings requiring the skill.
Bars sorted descending by count.

**How to Read**: Longer bars = more jobs demand that skill.

**Insight**: **Python, SQL, and PyTorch** dominate demand, appearing in over 60% of postings.
**LangChain and RAG-related skills** are emerging rapidly, appearing in ~18% of postings
— signalling the industry shift toward LLM-based application development.
```

#### Scatter Plot

```markdown
#### Salary vs. Experience — Scatter Plot with Regression Line
*Library: seaborn | Type: Scatter + regplot*

**Chart**: X-axis = years of experience (encoded), Y-axis = salary (USD).
Each dot = one job posting. Blue line = linear regression fit. Shaded band = 95% CI.

**How to Read**: The upward slope confirms a positive relationship.
Wide confidence bands at extremes reflect fewer data points there.

**Insight**: Salary increases approximately **$18,500 per experience tier** (Entry → Mid → Senior).
Scatter at the Senior level is wide, confirming that factors beyond experience (industry,
company size, specialization) create high variability at the top of the market.
```

#### Line Chart (Time Series)

```markdown
#### Monthly Job Postings Volume — Line Chart
*Library: plotly | Type: Line Chart*

**Chart**: X-axis = month (Jan 2024 – Dec 2025), Y-axis = number of job postings.
Hover tooltip displays exact count per month.

**How to Read**: Rising line = increasing hiring activity. Dips may correlate with
seasonal slowdowns or macroeconomic events.

**Insight**: Job posting volume peaked in **Q1 2025 (+34% YoY)** before a slight pullback
in Q3 2025, likely related to budget cycles. The overall trend remains strongly upward.
```

---

### 1.4 Writing Rules for Markdown Reports

- **Use headers** to separate each analysis section clearly.
- **Bold key numbers and takeaways** so skimmers can extract value quickly.
- **Avoid jargon** without explanation — define every statistical term on first use.
- **Include tables** for comparative data (salary by industry, skill counts, etc.).
- **Link chart images** with descriptive alt text: `![Salary Histogram](outputs/figures/salary_hist.png)`.
- **State limitations**: mention data gaps, sampling bias, or assumptions made.
- Never say a chart is "interesting" without explaining *what* makes it interesting.

---

## Part 2: Jupyter Notebook Writing Guide (Kaggle-Friendly)

Notebooks (`.ipynb`) in this project are **compiled analysis reports** — finalized, clean, and self-contained. They are published to Kaggle and must be runnable on Kaggle's infrastructure without modification.

### 2.1 Kaggle Compatibility Requirements

| Requirement | Rule |
|-------------|------|
| **Dataset source** | Read from `/kaggle/input/` path when running on Kaggle |
| **Local fallback** | Read from `data/raw/` when running locally |
| **No hardcoded secrets** | Never embed API keys or credentials |
| **No external file dependencies** | All required data must come from the Kaggle dataset or be generated in-notebook |
| **Self-contained installs** | Use `!pip install` cells for any non-standard packages |
| **Deterministic output** | Set random seeds; output must be identical on re-run |
| **Clear structure** | Kaggle readers browse notebooks linearly — every cell must be purposeful |

### 2.2 Dataset Source Declaration

Every notebook begins with a dataset declaration cell that documents where the data comes from and handles both local and Kaggle paths automatically.

```python
import os
from pathlib import Path

# ── Dataset Sources ────────────────────────────────────────────────────────────
# Kaggle dataset: https://www.kaggle.com/datasets/<owner>/<dataset-slug>
# Kaggle input path (when running on Kaggle):
#   /kaggle/input/<dataset-slug>/<filename>.csv
#
# Local path (when running locally):
#   data/raw/<filename>.csv
# ──────────────────────────────────────────────────────────────────────────────

KAGGLE_DATASET_PATH = Path("/kaggle/input/ai-job-market-insights/ai_job_market.csv")
LOCAL_DATASET_PATH  = Path("data/raw/ai_job_market.csv")

def resolve_dataset_path(kaggle_path: Path, local_path: Path) -> Path:
    """Return the correct dataset path depending on the runtime environment."""
    if kaggle_path.exists():
        return kaggle_path
    if local_path.exists():
        return local_path
    raise FileNotFoundError(
        f"Dataset not found.\n"
        f"  Kaggle path: {kaggle_path}\n"
        f"  Local path:  {local_path}\n"
        "Ensure the dataset is attached on Kaggle or present locally."
    )

DATASET_PATH = resolve_dataset_path(KAGGLE_DATASET_PATH, LOCAL_DATASET_PATH)
print(f"Using dataset: {DATASET_PATH}")
```

For notebooks that use **multiple datasets**, declare each one:

```python
# ── Multiple Dataset Sources ───────────────────────────────────────────────────
DATASETS = {
    "jobs": {
        "kaggle": Path("/kaggle/input/ai-job-market-insights/ai_job_market.csv"),
        "local":  Path("data/raw/ai_job_market.csv"),
    },
    "skills_index": {
        "kaggle": Path("/kaggle/input/tech-skills-index/skills.csv"),
        "local":  Path("data/external/skills.csv"),
    },
}

resolved = {
    key: resolve_dataset_path(paths["kaggle"], paths["local"])
    for key, paths in DATASETS.items()
}
```

### 2.3 Notebook Structure (Required Cell Order)

Every published notebook must follow this exact cell order:

```
[Markdown]  Title, Author, Date, Description, Objectives
[Markdown]  Table of Contents
[Python]    Package installs (non-standard only)
[Python]    Imports
[Python]    Configuration & constants (random seed, figure sizes, etc.)
[Python]    Dataset source declaration + path resolver
[Python]    Data loading
[Markdown]  ## 1. Dataset Overview
[Python]    Shape, dtypes, head(), describe()
[Markdown]  ## 2. Data Cleaning
[Python]    Cleaning steps
[Markdown]  ## 3. Exploratory Data Analysis
[Python]    Analysis + charts (one concept per cell)
[Markdown]  ## 4. Statistical Analysis
[Python]    Regression, correlation, segmentation
[Markdown]  ## 5. Key Insights
[Markdown]  ## 6. Conclusions & Recommendations
```

### 2.4 Title Cell Template

```markdown
# AI Job Market — Salary & Skills Analysis
**Author**: [Your Name]
**Date**: 2026-03-31
**Dataset**: [AI Job Market Insights](https://www.kaggle.com/datasets/owner/ai-job-market-insights)

---

## Description
This notebook analyzes AI job market postings to uncover salary trends, in-demand skills,
and the impact of experience level and industry on compensation.

## Objectives
1. Understand the salary distribution across AI roles
2. Identify the top in-demand technical skills
3. Quantify the effect of experience level on salary using regression
4. Segment salary outcomes by industry and location
```

### 2.5 Package Install Cell

Only install packages not available by default on Kaggle. Check Kaggle's pre-installed list first.

```python
# Install non-standard packages (skip if already available on Kaggle)
import subprocess, sys

EXTRA_PACKAGES = ["loguru", "pydantic>=2.0"]

for pkg in EXTRA_PACKAGES:
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])
```

### 2.6 Imports & Configuration Cell

```python
# ── Standard Library ──────────────────────────────────────────────────────────
import os
import warnings
from pathlib import Path

# ── Data Processing ───────────────────────────────────────────────────────────
import numpy as np
import pandas as pd

# ── Visualization ─────────────────────────────────────────────────────────────
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# ── Machine Learning ──────────────────────────────────────────────────────────
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error

warnings.filterwarnings("ignore")

# ── Global Configuration ──────────────────────────────────────────────────────
RANDOM_SEED   = 42
FIGURE_SIZE   = (12, 5)
PALETTE       = "viridis"
PLOTLY_THEME  = "plotly_white"

np.random.seed(RANDOM_SEED)

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", "{:,.2f}".format)

sns.set_theme(style="whitegrid", palette=PALETTE)
plt.rcParams.update({"figure.dpi": 120, "figure.figsize": FIGURE_SIZE})

print("Environment ready.")
```

### 2.7 Chart Writing Rules for Notebooks

Every chart cell must:
1. Be preceded by a **markdown cell** explaining what the chart will show and why.
2. Have a **descriptive title, labeled axes, and a legend** where applicable.
3. Include a **markdown cell after** the chart summarizing the key insight.
4. Use `plt.tight_layout()` for matplotlib/seaborn; `fig.show()` for plotly.
5. Save figures to `outputs/figures/` when running locally (skip on Kaggle).

```python
# Save figure helper — skips save when running on Kaggle
def save_figure(fig_name: str, dpi: int = 150) -> None:
    if not Path("/kaggle").exists():
        out = Path("outputs/figures")
        out.mkdir(parents=True, exist_ok=True)
        plt.savefig(out / fig_name, dpi=dpi, bbox_inches="tight")
```

**Example chart cell pattern:**

````markdown
### Salary Distribution by Experience Level

The box plot below shows how salary varies across Entry, Mid, and Senior experience levels.
This helps quantify the financial return of career progression in AI roles.
````

```python
fig, ax = plt.subplots(figsize=FIGURE_SIZE)

sns.boxplot(
    data=df,
    x="experience_level",
    y="salary_usd",
    order=["Entry", "Mid", "Senior"],
    palette=PALETTE,
    ax=ax,
)

ax.set_title("Salary Distribution by Experience Level", fontsize=14, fontweight="bold")
ax.set_xlabel("Experience Level")
ax.set_ylabel("Salary (USD)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

plt.tight_layout()
save_figure("salary_by_experience.png")
plt.show()
```

````markdown
**Insight**: Senior roles command a median salary ~$43K higher than Entry-level positions.
The wide IQR for Senior roles ($85K–$195K) reflects specialization premiums — senior ML
engineers at large tech companies earn significantly more than senior roles at smaller firms.
````

### 2.8 Statistical Analysis Cell Patterns

#### Descriptive Statistics

```python
salary_stats = df["salary_usd"].agg(
    Mean="mean",
    Median="median",
    Std="std",
    P25=lambda x: x.quantile(0.25),
    P75=lambda x: x.quantile(0.75),
    IQR=lambda x: x.quantile(0.75) - x.quantile(0.25),
)
salary_stats.map(lambda x: f"${x:,.0f}").to_frame("Salary (USD)").T
```

#### Regression Analysis

```python
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score

# Encode categoricals
le = LabelEncoder()
df_model = df.copy()
for col in ["experience_level", "industry", "company_size", "employment_type"]:
    df_model[col + "_enc"] = le.fit_transform(df_model[col].astype(str))

features = ["experience_level_enc", "industry_enc", "company_size_enc"]
X = df_model[features]
y = df_model["salary_usd"]

model = LinearRegression().fit(X, y)
y_pred = model.predict(X)

print(f"R² Score      : {r2_score(y, y_pred):.4f}")
print(f"MAE           : ${mean_absolute_error(y, y_pred):,.0f}")
print(f"\nCoefficients:")
for feat, coef in zip(features, model.coef_):
    print(f"  {feat:<30} {coef:+,.0f}")
```

#### Correlation Heatmap

```python
numeric_cols = df.select_dtypes(include="number").columns.tolist()
corr_matrix  = df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(10, 7))
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    linewidths=0.5,
    ax=ax,
)
ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold")
plt.tight_layout()
save_figure("correlation_heatmap.png")
plt.show()
```

### 2.9 Key Insights Cell Template

Use a markdown cell — never a code cell — for final insights:

```markdown
## 5. Key Insights

| # | Finding | Implication |
|---|---------|-------------|
| 1 | Median AI salary is $98,200 | Competitive baseline for job seekers |
| 2 | Tech sector pays 35% more than Education | Industry choice is a major salary lever |
| 3 | Python appears in 78% of postings | Non-negotiable skill for AI roles |
| 4 | Experience level drives salary more than company size (r=0.72 vs r=0.38) | Upskilling yields higher ROI than chasing big firms |
| 5 | LangChain / RAG skills +22% YoY demand growth | LLM integration is the fastest-growing specialization |
```

### 2.10 Notebook Submission Checklist (Kaggle)

Before publishing to Kaggle, verify every item:

- [ ] **Dataset path resolver** uses `resolve_dataset_path()` with both Kaggle and local paths
- [ ] **Dataset URL** is linked in the title cell
- [ ] **All cells run top-to-bottom** without errors (Kernel → Restart & Run All)
- [ ] **No hardcoded local paths** outside the path resolver function
- [ ] **Random seed** is set globally (`RANDOM_SEED = 42`)
- [ ] **All charts** have titles, axis labels, and a following insight cell
- [ ] **`!pip install` cell** present for any non-Kaggle-default packages
- [ ] **Output cells are cleared** before final submission, then re-run fresh
- [ ] **Notebook is < 20 MB** (Kaggle limit for notebooks without GPU)
- [ ] **No credentials or tokens** embedded anywhere in the notebook
- [ ] **All imports succeed** on a clean Kaggle Python environment

### 2.11 Notebook File Naming Convention

```
notebooks/
├── 01_exploration/
│   └── 01_eda_ai_job_market.ipynb
├── 02_cleaning/
│   └── 02_cleaning_ai_job_market.ipynb
├── 03_analysis/
│   └── 03_analysis_salary_regression.ipynb
│   └── 03_analysis_skills_demand.ipynb
└── 04_visuals/
    └── 04_visuals_dashboard.ipynb
```

- Prefix with section number (`01_`, `02_`, etc.)
- Use lowercase with underscores
- Be descriptive: include the analysis type in the name

---

## Quick Reference

### Markdown Report Checklist

- [ ] Each statistical term defined on first use
- [ ] Every chart has: type, library, axes description, how-to-read, and insight
- [ ] Key numbers are **bolded**
- [ ] Tables used for comparative data
- [ ] Outlier treatment is explicitly stated
- [ ] Limitations section included

### Notebook (Kaggle) Checklist

- [ ] `resolve_dataset_path()` handles both `/kaggle/input/` and local paths
- [ ] Dataset source URL documented in title cell
- [ ] Markdown insight cell follows every chart
- [ ] Runs cleanly with Kernel → Restart & Run All
- [ ] Random seed `42` set globally
- [ ] No credentials or hardcoded local paths

---

**Last Updated**: 2026-03-31
