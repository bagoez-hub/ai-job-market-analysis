# Data Analysis Guide — AI Job Market Analysis

## Project Overview

This is a **Python 3.14+** data analysis project analyzing the AI job market, built with modern Python practices and following reliable, reproducible, and maintainable data pipeline principles.

### Dataset Schema

The dataset (`data/raw/ai_job_market.csv`) contains the following columns:
- `job_id`: Unique identifier for each job posting
- `company_name`: Name of the hiring company
- `industry`: Industry sector
- `job_title`: Position title
- `skills_required`: Required skills (comma-separated or structured)
- `experience_level`: Required experience level (`Entry`, `Mid`, `Senior`, `Lead`, `Executive`)
- `employment_type`: Employment type (`Full-time`, `Part-time`, `Contract`, `Internship`)
- `location`: Job location
- `salary_range_usd`: Salary range in USD
- `posted_date`: Job posting date
- `company_size`: Size of the company (`Small`, `Medium`, `Large`, `Enterprise`)
- `tools_preferred`: Preferred tools/technologies

### Core Technologies
- **Python**: 3.14+
- **Data Validation**: Pydantic v2 for schema validation and serialization
- **Configuration**: pydantic-settings for type-safe configuration management
- **Data Processing**: pandas, numpy for core analysis
- **Visualization**: matplotlib, seaborn for statistical plots
- **Machine Learning**: scikit-learn for modeling and analysis
- **Logging**: loguru for structured logging
- **Testing**: pytest for unit and integration tests
- **Testing**: pytest-cov for coverage reporting
- **Notebooks**: Jupyter for exploratory analysis and reporting

## Analysis Vision

Build **reliable, reproducible, and maintainable** data pipelines that transform raw data into actionable insights. Our analysis follows these core principles:

1. **Idempotency First**: Same input always produces same output
2. **Data Quality Gates**: Validate at every stage with automated checks
3. **Configuration-Driven**: Use YAML/JSON configs over hardcoded logic
4. **Functional Approach**: Pure functions for data transformations
5. **Observable Pipelines**: Comprehensive logging and monitoring

## Tech Stack

### Core Framework
- **Python 3.14+**: Modern Python with latest type system enhancements

### Data & Validation
- **Pydantic v2**: Runtime type checking, validation, serialization
- **pydantic-settings**: Configuration management with environment variables
- **Great Expectations**: Data quality validation framework
- **Pandera**: DataFrame schema validation
- **dbt**: Data build tool for testing and documentation

### Data Processing
- **pandas**: Structured data manipulation
- **numpy**: Numerical computing
- **scipy**: Statistical analysis
- **scikit-learn**: Machine learning and analysis

### Orchestration (Recommended)
- **Airflow**: Workflow orchestration for complex pipelines
- **Prefect**: Modern dataflow automation
- **Dagster**: Data-aware orchestration platform

### Logging & Monitoring
- **loguru**: Simplified Python logging with better defaults
- **structlog**: Structured logging for production systems

### Development
- **pytest**: Testing framework
- **black**: Code formatter
- **ruff**: Fast Python linter
- **mypy**: Static type checker

### Visualization
- **matplotlib**: Core plotting library
- **seaborn**: Statistical data visualization
- **plotly**: Interactive visualizations

### Notebooks
- **Jupyter**: Exploratory data analysis and reporting

## Code Style

### Python Conventions
Follow **PEP 8** with modern enhancements:

```python
# ✅ Good: Type hints, clear naming, docstrings
from pydantic import BaseModel, Field

def clean_salary_data(
    raw_data: pd.DataFrame,
    min_salary: int = 0,
    max_salary: int | None = None
) -> pd.DataFrame:
    """
    Clean and validate salary data with range checks.
    
    Args:
        raw_data: Raw dataframe with salary columns
        min_salary: Minimum valid salary (default: 0)
        max_salary: Maximum valid salary (optional)
    
    Returns:
        Cleaned dataframe with validated salary data
    """
    cleaned = raw_data.copy()
    # Implementation here
    return cleaned
```

### Type Hints
- **Always use type hints** for function signatures
- Use built-in generics (Python 3.14+): `list[str]`, `dict[str, int]`, `str | None` — no `typing` imports needed
- Use `typing.Literal` for constrained string values
- For dataframes: `import pandas as pd` then use `pd.DataFrame` as type

```python
from typing import Literal
import pandas as pd

def aggregate_by_category(
    data: pd.DataFrame,
    group_by: list[str],
    agg_method: Literal["mean", "median", "sum"] = "mean"
) -> pd.DataFrame:
    """Aggregate data by specified grouping columns."""
    return data.groupby(group_by).agg(agg_method)
```

### Formatting Rules
- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Imports**: Organized with isort (stdlib → third-party → local)
- **Strings**: Double quotes preferred
- **Trailing commas**: Use in multi-line structures

```python
# Import organization
import os
from pathlib import Path
from typing import Dict, List

import pandas as pd
import numpy as np
from pydantic import BaseModel

from src.utils.logger import get_logger
from src.data.load_data import load_csv
```

## Folder Structure

```
ai_job_market/
├── config/                      # Configuration files
│   ├── config.yaml             # Main application config
│   ├── logging.yaml            # Logging configuration
│   └── paths.yaml              # Data paths configuration
├── data/
│   ├── raw/                    # Original, immutable data
│   ├── cleaned/                # Cleaned and validated data
│   ├── enriched/               # Feature-engineered data
│   ├── external/               # External reference data
│   └── dictionary/             # Data dictionaries, schemas
├── notebooks/                   # Jupyter notebooks
│   ├── 01_exploration/         # EDA notebooks
│   ├── 02_cleaning/            # Data cleaning notebooks
│   ├── 03_analysis/            # Statistical analysis
│   └── 04_visuals/             # Visualization notebooks
├── outputs/                     # Analysis outputs
│   ├── figures/                # Generated plots
│   ├── tables/                 # Summary tables
│   └── exports/                # Exported datasets
├── reports/                     # Generated reports
├── src/                         # Source code
│   ├── data/                   # Data pipeline modules
│   │   ├── load_data.py       # Data loading functions
│   │   ├── clean_data.py      # Data cleaning pipeline
│   │   ├── enrich.py          # Feature engineering
│   │   └── validate.py        # Data validation checks
│   ├── analysis/               # Analysis modules
│   │   ├── exploratory.py     # EDA functions
│   │   ├── kpi_analysis.py    # KPI calculations
│   │   ├── segmentation_analysis.py
│   │   └── forecasting_analysis.py
│   ├── visuals/                # Visualization modules
│   │   └── plot_utils.py      # Plotting utilities
│   └── utils/                  # Utility modules
│       ├── helpers.py          # Helper functions
│       └── logger.py           # Logging setup
└── tests/                       # Test suite
    ├── unit/                   # Unit tests
    ├── integration/            # Integration tests
    └── fixtures/               # Test fixtures
```

### File Naming
- **Python modules**: lowercase with underscores (`clean_data.py`)
- **Classes**: PascalCase (`DataValidator`)
- **Functions**: snake_case (`clean_salary_data`)
- **Constants**: UPPERCASE (`MAX_SALARY_THRESHOLD`)
- **Notebooks**: Numbered prefix (`01_exploratory_analysis.ipynb`)

## Pydantic Serialization

Use **Pydantic** for all data validation, serialization, and schema definition.

### Input Schemas
Define schemas for data loading and validation:

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Literal
from datetime import date

class JobRecordInput(BaseModel):
    """Schema for raw job market data input."""
    
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    job_title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    location: str
    job_type: Literal["Full-time", "Part-time", "Contract", "Freelance"]
    posted_date: date
    skills_required: list[str] = Field(default_factory=list)
    
    @field_validator("salary_max")
    @classmethod
    def validate_salary_range(cls, v, info):
        """Ensure max salary is greater than min salary."""
        if v is not None and info.data.get("salary_min"):
            if v < info.data["salary_min"]:
                raise ValueError("salary_max must be >= salary_min")
        return v
```

### Output Schemas
Define schemas for analysis results:

```python
from pydantic import BaseModel, Field
from typing import Dict, List

class SalaryStatistics(BaseModel):
    """Schema for salary analysis output."""
    
    category: str
    mean_salary: float = Field(..., ge=0)
    median_salary: float = Field(..., ge=0)
    std_dev: float = Field(..., ge=0)
    sample_size: int = Field(..., gt=0)
    percentile_25: float
    percentile_75: float
    
    model_config = ConfigDict(frozen=True)  # Immutable output

class AnalysisReport(BaseModel):
    """Schema for complete analysis report."""
    
    report_id: str
    generated_at: date
    salary_stats: List[SalaryStatistics]
    top_skills: Dict[str, int]
    summary: str
    
    def to_json_file(self, filepath: Path) -> None:
        """Export report to JSON file."""
        filepath.write_text(self.model_dump_json(indent=2))
```

### Configuration with pydantic-settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class DataConfig(BaseSettings):
    """Configuration for data pipeline."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DATA_",
        case_sensitive=False
    )
    
    raw_data_path: Path = Path("data/raw/ai_job_market.csv")
    cleaned_data_path: Path = Path("data/cleaned/")
    min_salary_threshold: int = 10000
    max_salary_threshold: int = 1000000
    enable_validation: bool = True

# Usage
config = DataConfig()
```

## Idempotency Patterns

**Idempotency**: Running the same operation multiple times with the same input produces the same result without side effects. Critical for reproducible analysis.

### Pure Functions
Write transformations as pure functions:

```python
# ✅ GOOD: Idempotent data transformation
def clean_salary_range(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pure function that always produces the same output for the same input.
    Does not modify the original DataFrame.
    """
    result = df.copy()

    # Deterministic operations only
    result['salary_min'] = result['salary_range_usd'].str.extract(r'(\d+)').astype(float)
    result['salary_max'] = result['salary_range_usd'].str.extract(r'-(\d+)').astype(float)

    return result

# ❌ BAD: Non-idempotent (in-place modification, timestamp dependency)
def clean_salary_range_bad(df: pd.DataFrame) -> None:
    df['processed_at'] = datetime.now()  # Non-deterministic
    df.drop_duplicates(inplace=True)     # In-place modification
```

**Best Practices**:
- Always create copies of DataFrames before transformation
- Avoid time-based operations unless necessary (use explicit timestamps from config)
- Use deterministic random seeds when sampling: `random_state=42`
- Version input data with checksums or hashes

**File Naming for Idempotency**:
```python
# Include version/timestamp in output filenames from config
output_file = f"cleaned_data_v{config['version']}.csv"
# Or use input file hash
output_file = f"cleaned_data_{hash(input_file)}.csv"
```

### Deterministic Processing

```python
# Always sort for consistent processing
def aggregate_by_category(data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate with deterministic ordering."""
    return (
        data
        .sort_values(["category", "date"])  # Explicit sort
        .groupby("category", sort=True)      # Ensure sorted groups
        .agg({"value": "mean"})
        .reset_index()
    )
```

### Immutable Data

```python
def clean_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Clean data without modifying input."""
    # ✅ Create copy, don't modify original
    cleaned = raw_data.copy()
    cleaned["salary"] = cleaned["salary"].fillna(0)
    return cleaned
```

### Function Composition

```python
from typing import Callable

def extract_salary_min(salary_str: str) -> float:
    """Extract minimum salary from range string."""
    match = re.search(r'(\d+)', salary_str)
    return float(match.group(1)) if match else None

def extract_salary_max(salary_str: str) -> float:
    """Extract maximum salary from range string."""
    match = re.search(r'-(\d+)', salary_str)
    return float(match.group(1)) if match else None

def add_salary_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add salary min/max columns. Pure function."""
    result = df.copy()
    result['salary_min'] = result['salary_range_usd'].apply(extract_salary_min)
    result['salary_max'] = result['salary_range_usd'].apply(extract_salary_max)
    result['salary_avg'] = (result['salary_min'] + result['salary_max']) / 2
    return result

def compose(*functions: Callable) -> Callable:
    """Compose multiple functions into a single function."""
    def inner(arg):
        result = arg
        for func in functions:
            result = func(result)
        return result
    return inner

# Usage: Chain transformations
pipeline = compose(
    remove_duplicates,
    standardize_column_names,
    add_salary_columns,
    categorize_experience
)
processed_df = pipeline(raw_df)
```

## Data Quality Checks

### Schema Validation with Pandera

```python
# src/data/validate.py
from pandera import DataFrameSchema, Column, Check

# Define schema expectations
job_market_schema = DataFrameSchema({
    'job_id': Column(str, nullable=False, unique=True),
    'company_name': Column(str, nullable=False),
    'salary_range_usd': Column(str, nullable=True),
    'experience_level': Column(str, Check.isin(['Entry', 'Mid', 'Senior', 'Lead', 'Executive'])),
    'employment_type': Column(str, Check.isin(['Full-time', 'Part-time', 'Contract', 'Internship'])),
    'posted_date': Column('datetime64[ns]', nullable=False),
    'company_size': Column(str, Check.isin(['Small', 'Medium', 'Large', 'Enterprise']))
})

def validate_raw_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Validate raw data against schema and business rules.
    Returns validated data and validation report.
    """
    report = {
        'total_rows': len(df),
        'null_counts': df.isnull().sum().to_dict(),
        'duplicate_ids': df['job_id'].duplicated().sum(),
        'date_range': (df['posted_date'].min(), df['posted_date'].max())
    }

    # Schema validation
    try:
        validated_df = job_market_schema.validate(df)
        report['schema_valid'] = True
    except Exception as e:
        report['schema_valid'] = False
        report['schema_errors'] = str(e)
        raise

    # Business rule validations
    assert df['salary_range_usd'].notna().sum() > len(df) * 0.5, \
        "More than 50% salary data missing"

    return validated_df, report
```

### Great Expectations Integration

```python
import great_expectations as gx
from great_expectations.dataset import PandasDataset

def validate_job_data(data: pd.DataFrame) -> bool:
    """Validate job data with Great Expectations."""
    ge_data = PandasDataset(data)

    # Define expectations
    ge_data.expect_column_values_to_not_be_null("job_title")
    ge_data.expect_column_values_to_be_between(
        "salary_min", min_value=0, max_value=1000000
    )
    ge_data.expect_column_values_to_be_in_set(
        "job_type", value_set=["Full-time", "Part-time", "Contract"]
    )

    # Validate
    results = ge_data.validate()
    return results.success
```

### Custom Validation Pipeline

```python
from typing import Callable, List
from loguru import logger

class DataValidator:
    """Pipeline for data quality checks."""

    def __init__(self):
        self.checks: List[Callable[[pd.DataFrame], bool]] = []

    def add_check(self, check: Callable[[pd.DataFrame], bool]) -> None:
        """Add validation check to pipeline."""
        self.checks.append(check)

    def validate(self, data: pd.DataFrame) -> bool:
        """Run all validation checks."""
        for i, check in enumerate(self.checks):
            try:
                if not check(data):
                    logger.error(f"Validation check {i} failed")
                    return False
            except Exception as e:
                logger.error(f"Validation check {i} raised error: {e}")
                return False

        logger.info(f"All {len(self.checks)} validation checks passed")
        return True

# Usage
validator = DataValidator()
validator.add_check(lambda df: df["salary_min"].notna().all())
validator.add_check(lambda df: (df["salary_min"] >= 0).all())
validator.validate(job_data)
```

### Quality Check Layers

1. **Raw Data Validation** (on load): Schema conformity, data type validation, required fields present, unique constraints
2. **Cleaning Validation** (post-cleaning): No unexpected nulls, value ranges within bounds, referential integrity, data distribution checks
3. **Enrichment Validation** (post-enrichment): New columns properly populated, no data loss from original records, derived metrics mathematically correct
4. **Output Validation** (before export): Final row count matches expectations, all required columns present, data types match schema

**Validation Configuration** (`config/validation.yaml`):
```yaml
validations:
  required_columns:
    - job_id
    - company_name
    - job_title
    - posted_date

  nullable_columns:
    - salary_range_usd
    - tools_preferred

  constraints:
    job_id:
      unique: true
    experience_level:
      allowed_values: ['Entry', 'Mid', 'Senior', 'Lead', 'Executive']
    employment_type:
      allowed_values: ['Full-time', 'Part-time', 'Contract', 'Internship']

  quality_thresholds:
    min_completeness: 0.80  # 80% of data should be present
    max_duplicates: 0.01    # Max 1% duplicate job_ids
```

## Orchestration

For complex workflows, use orchestration tools:

### Airflow Example (DAG Pattern)

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def load_raw_data():
    """Load raw data from source."""
    pass

def clean_data():
    """Clean and validate data."""
    pass

def run_analysis():
    """Execute analysis pipeline."""
    pass

with DAG(
    "job_market_analysis",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    load = PythonOperator(task_id="load", python_callable=load_raw_data)
    clean = PythonOperator(task_id="clean", python_callable=clean_data)
    analyze = PythonOperator(task_id="analyze", python_callable=run_analysis)

    load >> clean >> analyze
```

### Prefect Example (Flow Pattern)

```python
from prefect import flow, task
from pathlib import Path

@task(name="load_raw_data", retries=3)
def load_raw_data(config: dict) -> pd.DataFrame:
    """Load raw data from source."""
    file_path = Path(config['paths']['raw_data'])
    return pd.read_csv(file_path)

@task(name="clean_data")
def clean_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Clean and standardize data."""
    cleaned = df.copy()
    # ... cleaning logic ...
    return cleaned

@task(name="validate_data")
def validate_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Validate data quality."""
    validated, report = validate_raw_data(df)
    logger.info(f"Validation report: {report}")
    return validated

@task(name="enrich_data")
def enrich_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Enrich with derived features."""
    enriched = df.copy()
    # ... enrichment logic ...
    return enriched

@task(name="save_data")
def save_data(df: pd.DataFrame, output_path: str) -> None:
    """Save processed data."""
    df.to_csv(output_path, index=False)
    logger.info(f"Data saved to {output_path}")

@flow(name="ai_job_market_pipeline")
def data_pipeline(config_path: str = "config/config.yaml"):
    """Main data pipeline flow. Orchestrates the entire ETL process."""
    config = load_config(config_path)
    raw_data = load_raw_data(config)
    cleaned_data = clean_data(raw_data, config)
    validated_data = validate_data(cleaned_data, config)
    enriched_data = enrich_data(validated_data, config)
    save_data(enriched_data, config['paths']['enriched_data'])
    return enriched_data

if __name__ == "__main__":
    data_pipeline()
```

**Orchestration Best Practices**:
- Each task should be independently testable
- Use task-level retries for transient failures
- Implement checkpointing for long-running pipelines
- Log execution metadata (start time, end time, row counts)
- Use task dependencies to ensure correct execution order
- Implement failure notifications and alerts

## Code Structure Best Practices

### Module Organization

**`src/data/load_data.py`** — Data Loading:
```python
def load_raw_data(config: dict) -> pd.DataFrame:
    """Load raw data based on configuration."""
    pass

def load_external_data(source: str, config: dict) -> pd.DataFrame:
    """Load external reference data."""
    pass
```

**`src/data/clean_data.py`** — Data Cleaning:
```python
def remove_duplicates(df: pd.DataFrame, subset: list) -> pd.DataFrame:
    """Remove duplicate rows based on subset columns."""
    pass

def handle_missing_values(df: pd.DataFrame, strategy: str) -> pd.DataFrame:
    """Handle missing values based on strategy."""
    pass

def standardize_text_fields(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Standardize text fields (lowercase, strip, etc.)."""
    pass
```

**`src/data/enrich.py`** — Data Enrichment:
```python
def parse_skills(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Parse skills_required into structured format."""
    pass

def extract_salary_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract salary min, max, average."""
    pass

def add_temporal_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Add year, month, quarter, days_since_posted."""
    pass
```

**`src/data/validate.py`** — Data Validation:
```python
def validate_schema(df: pd.DataFrame, schema: dict) -> tuple:
    """Validate DataFrame against schema."""
    pass

def check_data_quality(df: pd.DataFrame, thresholds: dict) -> dict:
    """Check data quality metrics."""
    pass
```

**`src/analysis/exploratory.py`**:
```python
def generate_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Generate descriptive statistics."""
    pass

def analyze_missing_data(df: pd.DataFrame) -> dict:
    """Analyze missing data patterns."""
    pass
```

**`src/analysis/segmentation_analysis.py`**:
```python
def segment_by_category(df: pd.DataFrame, group_cols: list, metrics: list) -> pd.DataFrame:
    """Segment data by categorical variables."""
    pass

def identify_top_segments(df: pd.DataFrame, by: str, top_n: int = 10) -> pd.DataFrame:
    """Identify top N segments by specified metric."""
    pass
```

**`src/analysis/kpi_analysis.py`**:
```python
def calculate_kpis(df: pd.DataFrame, config: dict) -> dict:
    """Calculate key performance indicators."""
    pass
```

**`src/analysis/forecasting_analysis.py`**:
```python
def prepare_time_series(df: pd.DataFrame, date_col: str, value_col: str) -> pd.Series:
    """Prepare time series data for forecasting."""
    pass

def forecast_jobs(ts: pd.Series, horizon: int, model: str) -> pd.DataFrame:
    """Forecast future job postings."""
    pass
```

**`src/visuals/plot_utils.py`**:
```python
def plot_distribution(data: pd.Series, title: str, config: dict) -> None:
    """Plot distribution of a variable."""
    pass

def plot_trend(df: pd.DataFrame, x: str, y: str, title: str, config: dict) -> None:
    """Plot time series trend."""
    pass

def save_figure(fig, filename: str, config: dict) -> None:
    """Save figure to outputs/figures/."""
    pass
```

## Testing

### Unit Tests with pytest

```python
import pytest
import pandas as pd
from src.data.clean_data import clean_salary_data, remove_duplicates, handle_missing_values

def test_clean_salary_data_removes_outliers():
    """Test that outliers are properly removed."""
    # Arrange
    data = pd.DataFrame({
        "salary": [50000, 60000, 5000000, 70000]  # 5M is outlier
    })

    # Act
    result = clean_salary_data(data, max_salary=1000000)

    # Assert
    assert len(result) == 3
    assert result["salary"].max() <= 1000000

def test_clean_salary_data_handles_null():
    """Test null handling in salary data."""
    data = pd.DataFrame({"salary": [50000, None, 70000]})
    result = clean_salary_data(data)

    assert result["salary"].notna().all()

def test_remove_duplicates_idempotent():
    """Test that remove_duplicates is idempotent."""
    df = pd.DataFrame({'job_id': [1, 1, 2], 'title': ['A', 'A', 'B']})

    result1 = remove_duplicates(df, subset=['job_id'])
    result2 = remove_duplicates(result1, subset=['job_id'])

    pd.testing.assert_frame_equal(result1, result2)
    assert len(result1) == 2

def test_handle_missing_values_pure():
    """Test that handle_missing_values doesn't modify input."""
    df = pd.DataFrame({'salary': [50000, None, 75000]})
    df_copy = df.copy()

    result = handle_missing_values(df, strategy='median')

    pd.testing.assert_frame_equal(df, df_copy)  # Original unchanged
    assert result['salary'].notna().all()

@pytest.fixture
def sample_job_data():
    """Fixture for sample job data."""
    return pd.DataFrame({
        "job_title": ["Data Scientist", "ML Engineer"],
        "salary": [100000, 120000],
        "location": ["NYC", "SF"]
    })

def test_aggregate_by_location(sample_job_data):
    """Test location aggregation."""
    result = aggregate_by_location(sample_job_data)
    assert len(result) == 2
    assert "salary_mean" in result.columns
```

### Integration Tests

```python
def test_full_pipeline_integration():
    """Test complete data pipeline end-to-end."""
    # Load
    raw_data = load_data("tests/fixtures/sample_data.csv")
    
    # Clean
    cleaned = clean_data(raw_data)
    
    # Validate
    assert validate_job_data(cleaned)
    
    # Analyze
    results = run_analysis(cleaned)
    
    # Assert final output
    assert results is not None
    assert "salary_stats" in results
```

## Logging

Use **loguru** for simplified, powerful logging:

### Basic Setup

```python
# src/utils/logger.py
from loguru import logger
import sys
from pathlib import Path

def setup_logger(log_level: str = "INFO") -> None:
    """Configure loguru logger."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with color
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File handler with rotation
    logger.add(
        Path("logs/app_{time:YYYY-MM-DD}.log"),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",  # New file at midnight
        retention="30 days",
        compression="zip"
    )

# Usage in modules
from src.utils.logger import logger

logger.info("Starting data load")
logger.debug(f"Processing {len(data)} records")
logger.warning("Missing values detected")
logger.error("Validation failed")
```

### Structured Logging

```python
from loguru import logger

def process_job_records(data: pd.DataFrame) -> pd.DataFrame:
    """Process job records with detailed logging."""
    
    logger.info("Starting job record processing", records=len(data))
    
    try:
        # Processing steps
        cleaned = clean_data(data)
        logger.info(
            "Data cleaning complete",
            input_records=len(data),
            output_records=len(cleaned),
            removed=len(data) - len(cleaned)
        )
        
        return cleaned
        
    except Exception as e:
        logger.exception("Processing failed")
        raise
```

### Context Managers

```python
from loguru import logger
import time

@logger.catch  # Automatic exception logging
def risky_operation():
    """Function that might fail."""
    raise ValueError("Something went wrong")

# Timing context
class LogExecutionTime:
    """Context manager to log execution time."""
    
    def __init__(self, operation: str):
        self.operation = operation
    
    def __enter__(self):
        self.start = time.time()
        logger.info(f"Starting {self.operation}")
        return self
    
    def __exit__(self, *args):
        duration = time.time() - self.start
        logger.info(f"Completed {self.operation}", duration_seconds=duration)

# Usage
with LogExecutionTime("data pipeline"):
    process_data()
```

## Debugging

### Development Shortcuts

```python
# Quick data inspection
from IPython.display import display
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

def inspect(data: pd.DataFrame, name: str = "data") -> None:
    """Quick data inspection helper."""
    logger.info(f"Inspecting {name}")
    print(f"\n{'='*50}")
    print(f"Shape: {data.shape}")
    print(f"Columns: {list(data.columns)}")
    print(f"\nDtypes:\n{data.dtypes}")
    print(f"\nNull counts:\n{data.isnull().sum()}")
    print(f"\nFirst 5 rows:")
    display(data.head())
    print(f"{'='*50}\n")
```

### Django Debug Toolbar

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### Breakpoint Debugging

```python
def complex_transformation(data: pd.DataFrame) -> pd.DataFrame:
    """Complex data transformation."""
    
    # Set breakpoint for inspection
    breakpoint()  # Python 3.7+
    
    result = data.transform(...)
    return result
```

### Profiling

```python
import cProfile
import pstats

def profile_function(func):
    """Decorator to profile function execution."""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(20)
        
        return result
    return wrapper

@profile_function
def expensive_operation(data: pd.DataFrame):
    """Operation to profile."""
    return data.apply(lambda x: x ** 2)
```

## Notebook Writing

### Best Practices

1. **Structure**: Use clear markdown sections (Level 1-3 headings)
2. **One Cell, One Purpose**: Each cell should do one thing
3. **Imports First**: All imports in the first code cell
4. **Configuration Section**: Define constants early
5. **Visualization Standards**: Consistent styling across plots
6. **Document Assumptions**: Clearly state data assumptions and limitations

### Notebook Template

```python
# Cell 1: Title and Description
"""
# Job Market Analysis - Exploratory Data Analysis
**Author**: Data Science Team
**Date**: 2026-03-30
**Description**: Initial exploration of AI job market dataset

## Objectives
1. Understand data structure and quality
2. Identify salary distributions by role
3. Analyze geographic trends
4. Detect anomalies and outliers
"""

# Cell 2: Imports
from __future__ import annotations
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from loguru import logger

# Local imports
from src.data.load_data import load_csv
from src.utils.helpers import inspect

# Configure display
pd.set_option('display.max_columns', None)
%matplotlib inline
sns.set_style("whitegrid")

# Cell 3: Configuration
CONFIG = {
    "data_path": Path("data/raw/ai_job_market.csv"),
    "figure_size": (12, 6),
    "color_palette": "viridis",
    "random_seed": 42
}

logger.info("Configuration loaded", **CONFIG)

# Cell 4: Load Data
data = load_csv(CONFIG["data_path"])
inspect(data, "raw_job_data")

# Cell 5: Data Quality Check
"""
## Data Quality Assessment
"""
quality_report = {
    "total_records": len(data),
    "missing_values": data.isnull().sum().to_dict(),
    "duplicate_rows": data.duplicated().sum(),
    "data_types": data.dtypes.to_dict()
}

logger.info("Quality check complete", **quality_report)
display(pd.DataFrame([quality_report]))

# Cell 6: Analysis
"""
## Salary Distribution Analysis
"""
fig, ax = plt.subplots(figsize=CONFIG["figure_size"])
sns.histplot(data["salary"], bins=30, kde=True, ax=ax)
ax.set_title("Salary Distribution", fontsize=14, fontweight="bold")
ax.set_xlabel("Salary ($)")
ax.set_ylabel("Frequency")
plt.tight_layout()
plt.show()

# Cell 7: Summary and Next Steps
"""
## Key Findings
1. Dataset contains X records with Y features
2. Salary range: $Z to $W
3. Missing data: A% in column B

## Next Steps
1. Clean missing salary values
2. Remove outliers beyond 3 standard deviations
3. Enrich with industry classification
"""
```

### Notebook Organization

- **01_exploration/**: Initial EDA, data profiling
- **02_cleaning/**: Data cleaning, validation logic
- **03_analysis/**: Statistical analysis, modeling
- **04_visuals/**: Final visualizations for reports

### Export to Python Modules

Convert stable notebook code to modules:

```bash
# Export notebook to Python script
jupyter nbconvert --to script notebook.ipynb

# Then refactor into src/ modules
```

## Configuration-Driven Development

**Principle**: Behavior controlled by YAML/JSON configs, not hardcoded logic.

### YAML Configuration

```yaml
# config/config.yaml
version: "1.0.0"

project:
  name: "AI Job Market Analysis"
  description: "Analysis of AI/ML job market trends"

data:
  raw_file: "data/raw/ai_job_market.csv"
  cleaned_file: "data/cleaned/ai_job_market_cleaned.csv"
  enriched_file: "data/enriched/ai_job_market_enriched.csv"

  encoding: "utf-8"
  delimiter: ","

  date_columns:
    - posted_date

  categorical_columns:
    - industry
    - experience_level
    - employment_type
    - company_size

processing:
  remove_duplicates:
    enabled: true
    subset: ['job_id']

  handle_missing:
    strategy: "default"  # default, drop, impute
    impute_method: "median"
    threshold: 0.5  # Drop columns with >50% missing

  outlier_detection:
    enabled: true
    method: "iqr"  # iqr, zscore, isolation_forest
    threshold: 3.0

features:
  salary:
    extract_min: true
    extract_max: true
    calculate_avg: true
    normalize: true

  skills:
    parse_method: "comma_split"
    max_skills: 10
    create_dummies: true

  date:
    extract_year: true
    extract_month: true
    extract_quarter: true
    calculate_days_since_posted: true

analysis:
  segmentation:
    group_by:
      - experience_level
      - industry
      - company_size

    metrics:
      - mean_salary
      - median_salary
      - job_count
      - top_skills

  forecasting:
    enabled: true
    target: "job_count"
    time_column: "posted_date"
    frequency: "M"  # Monthly
    horizon: 12  # 12 months ahead
    model: "prophet"  # prophet, arima, exponential_smoothing

visualization:
  style: "seaborn"
  palette: "viridis"
  figure_dpi: 300
  save_format: "png"

  plots:
    - type: "distribution"
      column: "salary_avg"
      title: "Salary Distribution"

    - type: "trend"
      x: "posted_date"
      y: "job_count"
      title: "Job Posting Trends Over Time"

    - type: "heatmap"
      values: "skills_required"
      title: "Top Skills by Industry"

output:
  exports:
    - format: "csv"
      path: "outputs/exports/ai_jobs_summary.csv"

    - format: "parquet"
      path: "outputs/exports/ai_jobs_summary.parquet"
      compression: "snappy"

  reports:
    generate_html: true
    include_plots: true
    template: "reports/template.html"
```

### Load Config

```python
# src/utils/helpers.py
import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Any

def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def get_config_value(config: dict, key_path: str, default: Any = None) -> Any:
    """
    Get nested config value using dot notation.
    Example: get_config_value(config, 'processing.remove_duplicates.enabled')
    """
    keys = key_path.split('.')
    value = config

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value

# Pydantic-based typed config loading
class DataPaths(BaseModel):
    raw_path: Path
    cleaned_path: Path

class ValidationConfig(BaseModel):
    min_salary: int
    max_salary: int
    required_columns: list[str]

class AppConfig(BaseModel):
    data: DataPaths
    validation: ValidationConfig

def load_typed_config(config_path: Path = Path("config/config.yaml")) -> AppConfig:
    """Load configuration with Pydantic type validation."""
    with open(config_path) as f:
        config_dict = yaml.safe_load(f)
    return AppConfig(**config_dict)
```

---

## Workflow Example: Complete Pipeline

```python
# main.py
import sys
from pathlib import Path
from src.utils.helpers import load_config
from src.utils.logger import setup_logger
from src.data.load_data import load_raw_data
from src.data.clean_data import clean_pipeline
from src.data.validate import validate_schema, check_data_quality
from src.data.enrich import enrich_pipeline
from src.analysis.exploratory import generate_summary_statistics
from src.visuals.plot_utils import create_visualizations

logger = setup_logger(__name__)

def main(config_path: str = "config/config.yaml"):
    """Main pipeline execution."""
    logger.info("=" * 50)
    logger.info("Starting AI Job Market Analysis Pipeline")
    logger.info("=" * 50)

    # 1. Load configuration
    config = load_config(config_path)
    logger.info(f"Configuration loaded: version {config['version']}")

    # 2. Load raw data (idempotent)
    raw_df = load_raw_data(config)
    logger.info(f"Loaded {len(raw_df)} records")

    # 3. Clean data (pure functions)
    cleaned_df = clean_pipeline(raw_df, config)
    logger.info(f"Cleaned data: {len(cleaned_df)} records")

    # 4. Validate data quality
    validation_report = check_data_quality(cleaned_df, config['validations'])
    if not validation_report['passed']:
        logger.error("Data quality validation failed")
        sys.exit(1)

    # 5. Enrich data (pure functions)
    enriched_df = enrich_pipeline(cleaned_df, config)
    logger.info(f"Enriched data with {len(enriched_df.columns)} features")

    # 6. Save processed data
    output_path = Path(config['data']['enriched_file'])
    enriched_df.to_csv(output_path, index=False)
    logger.info(f"Saved enriched data to {output_path}")

    # 7. Generate analysis and visualizations
    summary_stats = generate_summary_statistics(enriched_df)
    create_visualizations(enriched_df, config)

    logger.info("=" * 50)
    logger.info("Pipeline completed successfully")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
```

## Key Takeaways

1. **Idempotency**: Always use pure functions that don't modify input data
2. **Data Quality**: Validate at every stage with automated checks
3. **Orchestration**: Structure work as composable, retryable tasks
4. **Functional Style**: Prefer pure functions and immutability
5. **Configuration**: Drive behavior from YAML configs, not hardcoded values
6. **Testing**: Write tests for all transformations to ensure correctness
7. **Logging**: Comprehensive logging for debugging and monitoring
8. **Documentation**: Config files serve as living documentation

## Common Patterns

### ETL Pipeline
```
Load (config-driven) → Clean (pure functions) → Validate (quality checks)
→ Enrich (pure functions) → Validate (quality checks) → Save (versioned)
```

### Analysis Workflow
```
Load processed data → Group/Segment (config-driven) → Calculate metrics (pure)
→ Visualize (config-driven) → Export results (versioned)
```

### Incremental Processing
```
Check if output exists → Compare input hash → Skip if unchanged → Process only new data
```

---

## Quick Reference

### Common Commands

```bash
# Format code
black src/ notebooks/

# Lint code
ruff check src/

# Type check
mypy src/

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific notebook
jupyter notebook notebooks/01_exploration/initial_eda.ipynb
```

### Key Principles Checklist

- [ ] Functions are pure and deterministic (idempotency)
- [ ] Type hints on all function signatures
- [ ] Pydantic schemas for inputs/outputs
- [ ] Data quality checks with Great Expectations
- [ ] Structured logging with loguru
- [ ] Configuration driven (no hardcoded values)
- [ ] Comprehensive tests (unit + integration)
- [ ] Proper error handling and validation
- [ ] Clear documentation and docstrings
- [ ] Reproducible results (fixed random seeds)

---

**Last Updated**: 2026-03-31
