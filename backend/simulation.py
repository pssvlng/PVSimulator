"""
Simulation management for PV Simulator
"""
import os
import csv
import json
import time
import threading
import logging
from datetime import datetime
from typing import List
import numpy as np
import pika

from config import config
from models import MeterReading, PVData
from utils import get_rabbitmq_connection, pv_profile

logger = logging.getLogger(__name__)


class SimulationManager:
    """Manages the PV simulation with thread-safe operations"""
    
    def __init__(self):
        self._running = threading.Event()
        self._shutdown = threading.Event()
        self._threads: List[threading.Thread] = []
        self._lock = threading.Lock()
        
    def start(self) -> bool:
        """
        Start the simulation with meter and PV worker threads
        
        Returns:
            True if simulation started successfully, False if already running
        """
        with self._lock:
            if self._running.is_set():
                return False
            
            self._running.set()
            self._shutdown.clear()
            
            # Start threads
            meter_thread = threading.Thread(target=self._meter_worker, daemon=False)
            pv_thread = threading.Thread(target=self._pv_worker, daemon=False)
            
            self._threads = [meter_thread, pv_thread]
            
            for thread in self._threads:
                thread.start()
            
            logger.info("Simulation started successfully")
            return True
    
    def stop(self) -> bool:
        """
        Stop the simulation gracefully
        
        Returns:
            True if simulation stopped successfully, False if not running
        """
        with self._lock:
            if not self._running.is_set():
                return False
            
            self._running.clear()
            self._shutdown.set()
            
            # Wait for threads to finish gracefully
            for thread in self._threads:
                thread.join(timeout=10)
            
            self._threads.clear()
            logger.info("Simulation stopped successfully")
            return True
    
    @property
    def is_running(self) -> bool:
        """Check if simulation is currently running"""
        return self._running.is_set()
    
    def _meter_worker(self):
        """Meter thread: sends random values to RabbitMQ"""
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            channel.queue_declare(queue=config.METER_QUEUE, durable=True)
            
            logger.info("Meter worker started")
            
            while self._running.is_set():
                try:
                    value = round(np.random.uniform(0.5, 10.0), 2)
                    timestamp = datetime.now().isoformat()
                    
                    # Validate data
                    reading = MeterReading(timestamp=datetime.fromisoformat(timestamp), meter=value)
                    
                    msg = json.dumps({'timestamp': timestamp, 'meter': value})
                    channel.basic_publish(
                        exchange='', 
                        routing_key=config.METER_QUEUE, 
                        body=msg, 
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    
                    logger.debug(f"Sent meter reading: {value} kW")
                    time.sleep(config.METER_INTERVAL)
                    
                except Exception as e:
                    logger.error(f"Error in meter worker: {e}")
                    time.sleep(1)
                    
            connection.close()
            logger.info("Meter worker stopped")
        except Exception as e:
            logger.error(f"Meter worker error: {e}")
    
    def _pv_worker(self):
        """PV Simulator thread: listens for meter values, calculates PV, writes results"""
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            channel.queue_declare(queue=config.METER_QUEUE, durable=True)
            
            # Initialize CSV file with headers if not exists
            if not os.path.exists(config.RESULTS_FILE):
                with open(config.RESULTS_FILE, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'meter', 'pv', 'sum'])
                logger.info("Created new results CSV file")
            
            logger.info("PV worker started")
            
            def callback(ch, method, properties, body):
                if not self._running.is_set():
                    return
                    
                try:
                    data = json.loads(body)
                    timestamp = data['timestamp']
                    meter = float(data['meter'])
                    
                    # Calculate PV based on current time
                    current_time = datetime.fromisoformat(timestamp)
                    hour = current_time.hour
                    minute = current_time.minute
                    pv = round(pv_profile(hour, minute), 2)
                    
                    # Calculate net power (PV production - meter consumption)
                    # This represents net power fed back to grid (positive) or drawn from grid (negative)
                    total = round(pv - meter, 2)
                    
                    # Validate data
                    pv_data = PVData(
                        timestamp=current_time,
                        meter=meter,
                        pv=pv,
                        net=total
                    )
                    
                    # Write to CSV with file locking
                    with open(config.RESULTS_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, meter, pv, total])
                    
                    logger.debug(f"Processed: meter={meter}, pv={pv}, sum={total}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            channel.basic_consume(queue=config.METER_QUEUE, on_message_callback=callback)
            
            while self._running.is_set():
                connection.process_data_events(time_limit=1)
                
            connection.close()
            logger.info("PV worker stopped")
        except Exception as e:
            logger.error(f"PV worker error: {e}")
