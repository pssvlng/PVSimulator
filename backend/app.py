import os
import threading
import time
import json
import csv
from datetime import datetime
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import pika
import numpy as np

app = Flask(__name__)
CORS(app)

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'user')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'password')
METER_QUEUE = 'meter_queue'
RESULTS_FILE = 'results.csv'

# Global simulation state
simulation_running = False
meter_thread_obj = None
pv_thread_obj = None

# Helper: Bell curve for PV simulation
def pv_profile(hour, minute=0):
    # Simulate PV output as a bell curve (Gaussian) with more realistic curve
    time_decimal = hour + minute / 60.0
    peak_hour = 12.0  # Solar noon
    return max(0, 8 * np.exp(-((time_decimal - peak_hour)**2) / 18))

# Meter thread: sends random values to RabbitMQ
def meter_thread():
    global simulation_running
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=METER_QUEUE, durable=True)
        
        while simulation_running:
            value = round(np.random.uniform(0.5, 10.0), 2)
            timestamp = datetime.now().isoformat()
            msg = json.dumps({'timestamp': timestamp, 'meter': value})
            channel.basic_publish(exchange='', routing_key=METER_QUEUE, body=msg, 
                                properties=pika.BasicProperties(delivery_mode=2))
            time.sleep(3)  # Send data every 3 seconds
            
        connection.close()
    except Exception as e:
        print(f"Meter thread error: {e}")

# PV Simulator thread: listens for meter values, calculates PV, writes results
def pv_simulator_thread():
    global simulation_running
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=METER_QUEUE, durable=True)
        
        # Initialize CSV file with headers if not exists
        if not os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'meter', 'pv', 'sum'])
        
        def callback(ch, method, properties, body):
            if not simulation_running:
                return
                
            data = json.loads(body)
            timestamp = data['timestamp']
            meter = float(data['meter'])
            
            # Calculate PV based on current time
            current_time = datetime.fromisoformat(timestamp)
            hour = current_time.hour
            minute = current_time.minute
            pv = round(pv_profile(hour, minute), 2)
            
            # Sum values (meter consumption + PV production)
            total = round(meter + pv, 2)
            
            # Write to CSV
            with open(RESULTS_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, meter, pv, total])
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        channel.basic_consume(queue=METER_QUEUE, on_message_callback=callback)
        
        while simulation_running:
            connection.process_data_events(time_limit=1)
            
        connection.close()
    except Exception as e:
        print(f"PV simulator thread error: {e}")

# API endpoints
@app.route('/start', methods=['POST'])
def start_simulation():
    global simulation_running, meter_thread_obj, pv_thread_obj
    
    if simulation_running:
        return jsonify({'status': 'already running', 'running': True})
    
    simulation_running = True
    meter_thread_obj = threading.Thread(target=meter_thread, daemon=True)
    pv_thread_obj = threading.Thread(target=pv_simulator_thread, daemon=True)
    
    meter_thread_obj.start()
    pv_thread_obj.start()
    
    return jsonify({'status': 'started', 'running': True})

@app.route('/stop', methods=['POST'])
def stop_simulation():
    global simulation_running
    simulation_running = False
    return jsonify({'status': 'stopped', 'running': False})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({'running': simulation_running})

@app.route('/results', methods=['GET'])
def get_results():
    if not os.path.exists(RESULTS_FILE):
        return jsonify([])
    
    try:
        with open(RESULTS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
            
        # Convert string values to float for frontend
        for result in results:
            result['meter'] = float(result['meter'])
            result['pv'] = float(result['pv'])
            result['sum'] = float(result['sum'])
            
        return jsonify(results)
    except Exception as e:
        return jsonify([])

@app.route('/results/latest', methods=['GET'])
def get_latest_results():
    """Get the latest 50 results for real-time chart updates"""
    if not os.path.exists(RESULTS_FILE):
        return jsonify([])
    
    try:
        with open(RESULTS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
            
        # Get latest 50 entries
        latest_results = results[-50:] if len(results) > 50 else results
        
        # Convert string values to float for frontend
        for result in latest_results:
            result['meter'] = float(result['meter'])
            result['pv'] = float(result['pv'])
            result['sum'] = float(result['sum'])
            
        return jsonify(latest_results)
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
