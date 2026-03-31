import sys
from pathlib import Path

from loguru import logger


def setup_logger(log_level: str = "INFO", log_dir: str = "logs") -> None:
    """
    Configure loguru with a console handler and a rotating file handler.

    Args:
        log_level: Minimum level for the console handler (default: INFO).
        log_dir: Directory where daily log files are written (default: logs/).
    """
    logger.remove()

    # Console handler — colourised, INFO and above
    logger.add(
        sys.stdout,
        level=log_level,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )

    # File handler — DEBUG and above, daily rotation, 30-day retention
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_path / "app_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",
        retention="30 days",
        compression="zip",
    )


def get_logger():
    """Return the configured loguru logger instance."""
    return logger

