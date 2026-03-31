from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import yaml

from src.utils.logger import get_logger

logger = get_logger()


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------


def load_config(config_path: str | Path = "config/config.yaml") -> dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Parsed configuration as a nested dictionary.
    """
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as fh:
        config: dict[str, Any] = yaml.safe_load(fh)
    logger.debug(f"Configuration loaded from {path}")
    return config


def get_config_value(
    config: dict[str, Any],
    key_path: str,
    default: Any = None,
) -> Any:
    """
    Retrieve a nested configuration value using dot notation.

    Example:
        get_config_value(config, "processing.remove_duplicates.enabled")

    Args:
        config: Loaded configuration dictionary.
        key_path: Dot-separated path to the desired key.
        default: Value returned when the key is not found.

    Returns:
        The value at the specified path, or *default* if not found.
    """
    keys = key_path.split(".")
    value: Any = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


# ---------------------------------------------------------------------------
# DataFrame inspection
# ---------------------------------------------------------------------------


def inspect(data: pd.DataFrame, name: str = "data") -> None:
    """
    Print a concise summary of a DataFrame for quick EDA.

    Args:
        data: DataFrame to inspect.
        name: Label displayed in the summary header.
    """
    logger.info(f"Inspecting '{name}' — shape: {data.shape}")
    border = "=" * 60
    print(f"\n{border}")
    print(f"  {name}  ({data.shape[0]:,} rows × {data.shape[1]} cols)")
    print(border)
    print(f"\nDtypes:\n{data.dtypes.to_string()}")
    print(f"\nNull counts:\n{data.isnull().sum().to_string()}")
    print(f"\nFirst 5 rows:\n{data.head().to_string()}")
    print(f"{border}\n")


# ---------------------------------------------------------------------------
# Function composition
# ---------------------------------------------------------------------------


def compose(*functions: Callable) -> Callable:
    """
    Compose multiple single-argument functions into one pipeline.

    Functions are applied left-to-right:
        compose(f, g, h)(x)  ≡  h(g(f(x)))

    Args:
        *functions: Ordered sequence of callables to compose.

    Returns:
        A new callable that threads its argument through all functions.
    """

    def pipeline(arg: Any) -> Any:
        result = arg
        for func in functions:
            result = func(result)
        return result

    return pipeline


# ---------------------------------------------------------------------------
# Execution timing
# ---------------------------------------------------------------------------


class LogExecutionTime:
    """Context manager that logs the wall-clock duration of a block."""

    def __init__(self, operation: str) -> None:
        self.operation = operation
        self._start: float = 0.0

    def __enter__(self) -> "LogExecutionTime":
        self._start = time.perf_counter()
        logger.info(f"Starting — {self.operation}")
        return self

    def __exit__(self, *args: object) -> None:
        duration = time.perf_counter() - self._start
        logger.info(f"Completed — {self.operation} ({duration:.2f}s)")

