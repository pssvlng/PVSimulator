import os
import sys
import signal
import atexit
import time
import csv
from datetime import datetime

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from config import config
from models import MeterReading, PVData
from utils import get_rabbitmq_connection
from simulation import SimulationManager
from logging_config import setup_logging

# Ensure data directory exists
os.makedirs(config.DATA_DIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Configure logging
logger = setup_logging()

# Flask app setup
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
CORS(app)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

start_time = time.time()

# Initialize simulation manager
simulation_manager = SimulationManager()

# Graceful shutdown
def shutdown_handler(signum, frame):
    logger.info("Received shutdown signal, stopping simulation...")
    simulation_manager.stop()
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
atexit.register(lambda: simulation_manager.stop())

# API endpoints
@app.route('/start', methods=['POST'])
@limiter.limit("5 per minute")
def start_simulation():
    """Start the PV simulation"""
    if simulation_manager.is_running:
        return jsonify({'status': 'already running', 'running': True}), 200
    
    try:
        success = simulation_manager.start()
        if success:
            return jsonify({'status': 'started', 'running': True}), 200
        else:
            return jsonify({'status': 'failed to start', 'running': False}), 500
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        return jsonify({'status': 'error', 'message': str(e), 'running': False}), 500

@app.route('/stop', methods=['POST'])
@limiter.limit("10 per minute")
def stop_simulation():
    """Stop the PV simulation"""
    try:
        success = simulation_manager.stop()
        return jsonify({'status': 'stopped', 'running': False}), 200
    except Exception as e:
        logger.error(f"Error stopping simulation: {e}")
        return jsonify({'status': 'error', 'message': str(e), 'running': simulation_manager.is_running}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current simulation status"""
    return jsonify({
        'running': simulation_manager.is_running,
        'uptime': int(time.time() - start_time)
    })

@app.route('/results', methods=['GET'])
@limiter.limit("30 per minute")
def get_results():
    """Get all simulation results"""
    if not os.path.exists(config.RESULTS_FILE):
        return jsonify([])
    
    try:
        with open(config.RESULTS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
            
        # Convert string values to float for frontend
        for result in results:
            try:
                result['meter'] = float(result['meter'])
                result['pv'] = float(result['pv'])
                # Map 'sum' column to 'net' for frontend compatibility
                if 'sum' in result:
                    result['net'] = float(result['sum'])
                elif 'net' in result:
                    result['net'] = float(result['net'])
                else:
                    result['net'] = 0.0  # Fallback value
            except (ValueError, KeyError) as e:
                logger.warning(f"Error converting result data: {e}")
                continue
            
        logger.info(f"Returned {len(results)} results")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error reading results: {e}")
        return jsonify([])

@app.route('/results/latest', methods=['GET'])
@limiter.limit("60 per minute")
def get_latest_results():
    """Get the latest results for real-time chart updates"""
    if not os.path.exists(config.RESULTS_FILE):
        return jsonify([])
    
    try:
        with open(config.RESULTS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
            
        # Get latest entries based on config
        latest_results = results[-config.MAX_RESULTS_RETURNED:] if len(results) > config.MAX_RESULTS_RETURNED else results
        
        # Convert string values to float for frontend
        for result in latest_results:
            try:
                result['meter'] = float(result['meter'])
                result['pv'] = float(result['pv'])
                # Map 'sum' column to 'net' for frontend compatibility
                if 'sum' in result:
                    result['net'] = float(result['sum'])
                elif 'net' in result:
                    result['net'] = float(result['net'])
                else:
                    result['net'] = 0.0  # Fallback value
            except (ValueError, KeyError) as e:
                logger.warning(f"Error converting result data: {e}")
                continue
            
        return jsonify(latest_results)
    except Exception as e:
        logger.error(f"Error reading latest results: {e}")
        return jsonify([])

# Health check and monitoring endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration"""
    try:
        # Check RabbitMQ connection
        connection = get_rabbitmq_connection()
        connection.close()
        rabbitmq_status = "healthy"
    except Exception as e:
        logger.warning(f"RabbitMQ health check failed: {e}")
        rabbitmq_status = "unhealthy"
    
    # Check file system
    file_status = "healthy" if os.access(config.DATA_DIR, os.W_OK) else "unhealthy"
    
    status = {
        "status": "healthy" if all([rabbitmq_status == "healthy", file_status == "healthy"]) else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rabbitmq": rabbitmq_status,
            "filesystem": file_status,
            "simulation": "running" if simulation_manager.is_running else "stopped"
        }
    }
    
    return jsonify(status), 200 if status["status"] == "healthy" else 503

@app.route('/metrics', methods=['GET'])
def metrics():
    """Basic metrics endpoint"""
    try:
        file_size = os.path.getsize(config.RESULTS_FILE) if os.path.exists(config.RESULTS_FILE) else 0
        if os.path.exists(config.RESULTS_FILE):
            with open(config.RESULTS_FILE, 'r') as f:
                line_count = sum(1 for _ in f) - 1  # Exclude header
        else:
            line_count = 0
    except Exception as e:
        logger.warning(f"Error getting metrics: {e}")
        file_size = 0
        line_count = 0
    
    return jsonify({
        "simulation_running": simulation_manager.is_running,
        "data_points": line_count,
        "file_size_bytes": file_size,
        "uptime_seconds": int(time.time() - start_time),
        "config": {
            "meter_interval": config.METER_INTERVAL,
            "max_results_returned": config.MAX_RESULTS_RETURNED
        }
    })

if __name__ == '__main__':
    logger.info(f"Starting PV Simulator on {config.FLASK_HOST}:{config.FLASK_PORT}")
    logger.info(f"Debug mode: {config.FLASK_DEBUG}")
    logger.info(f"RabbitMQ: {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}")
    logger.info(f"Results file: {config.RESULTS_FILE}")
    
    try:
        app.run(
            host=config.FLASK_HOST, 
            port=config.FLASK_PORT, 
            debug=config.FLASK_DEBUG
        )
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        simulation_manager.stop()
    except Exception as e:
        logger.error(f"Application error: {e}")
        simulation_manager.stop()
        raise
