"""Structured logging setup for NexusRAG."""

from __future__ import annotations

import logging
import sys

from config.settings import get_settings


def configure_logging() -> logging.Logger:
    """Configure root logging once and return the application logger."""
    settings = get_settings()
    logger = logging.getLogger("nexusrag")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.propagate = False
    return logger
