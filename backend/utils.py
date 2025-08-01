"""
Utility functions for PV Simulator
"""
import time
import logging
import numpy as np
from functools import wraps
from typing import Callable, Any
import pika
from config import config

logger = logging.getLogger(__name__)


def pv_profile(hour: int, minute: int = 0) -> float:
    """
    Simulate PV output as a bell curve (Gaussian) with realistic curve
    
    Args:
        hour: Hour of the day (0-23)
        minute: Minute of the hour (0-59)
        
    Returns:
        PV power output in kW (0-8 kW max at solar noon)
    """
    time_decimal = hour + minute / 60.0
    peak_hour = 12.0  # Solar noon
    return max(0, 8 * np.exp(-((time_decimal - peak_hour)**2) / 18))


def retry_on_failure(max_retries: int = 3, delay: int = 5):
    """
    Decorator to retry function calls on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay in seconds between retries
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"All {max_retries} attempts failed")
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


@retry_on_failure(max_retries=5, delay=2)
def get_rabbitmq_connection():
    """Create RabbitMQ connection with retry logic"""
    credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
    )
    return pika.BlockingConnection(parameters)
