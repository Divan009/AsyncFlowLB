# logger.py

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
# Directory for log files
    log_dir: str = "logs",
    log_file: str = "loadbalancer.log",
    max_bytes: int = 10**6,  # 1MB
    backup_count: int = 5
):
    """
    Configures the logging for the application.

    :param log_level: Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :param log_format: Format string for log messages
    :param date_format: Format string for log timestamps
    :param log_file: File path for the log file
    :param max_bytes: Maximum size in bytes for the log file before rotation
    :param backup_count: Number of backup log files to keep
    """

    # Ensure the log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Full path for the log file
    full_log_file = log_path / log_file


    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler with Rotation
    file_handler = RotatingFileHandler(
        full_log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a logger with the specified name.

    :param name: Name of the logger
    :return: Configured logger instance
    """
    return logging.getLogger(name)
