import logging
from datetime import datetime
from typing import Optional


def setup_logger(name: str = "netra") -> logging.Logger:
    """
    Set up application logger.
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding duplicate handlers when called multiple times.
    # logging.getLogger(name) returns the same singleton instance, so without
    # this guard every call would append another handler and duplicate output.
    if logger.handlers:
        return logger

    # Prevent log records from bubbling up to the root logger (avoids duplicates)
    logger.propagate = False

    # Console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def log_module_start(logger: logging.Logger, module: str, domain: str):
    """Log module start."""
    logger.info(f"{module} Started - Domain: {domain}")


def log_module_complete(logger: logging.Logger, module: str, domain: str, execution_time: float):
    """Log module completion."""
    logger.info(f"{module} Completed - Domain: {domain} - Time: {execution_time:.2f}s")


def log_module_error(logger: logging.Logger, module: str, domain: str, error: str):
    """Log module error."""
    logger.error(f"{module} Failed - Domain: {domain} - Error: {error}")
