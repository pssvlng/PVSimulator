"""
Configuration management for PV Simulator
"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    # RabbitMQ settings
    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_USER: str = os.getenv('RABBITMQ_USER', 'user')
    RABBITMQ_PASS: str = os.getenv('RABBITMQ_PASS', 'password')
    RABBITMQ_PORT: int = int(os.getenv('RABBITMQ_PORT', '5672'))
    METER_QUEUE: str = os.getenv('METER_QUEUE', 'meter_queue')
    
    # App settings
    RESULTS_FILE: str = os.getenv('RESULTS_FILE', 'results.csv')
    DATA_DIR: str = os.getenv('DATA_DIR', './data')
    METER_INTERVAL: int = int(os.getenv('METER_INTERVAL', '3'))
    MAX_RESULTS_RETURNED: int = int(os.getenv('MAX_RESULTS_RETURNED', '50'))
    
    # Flask settings
    FLASK_HOST: str = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT: int = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'


# Global config instance
config = Config()
