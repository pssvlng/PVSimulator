import pytest
import json
import os
import tempfile
from unittest.mock import patch, Mock
from datetime import datetime

import app
from utils import pv_profile
from models import MeterReading, PVData
from config import config
from simulation import SimulationManager


@pytest.fixture
def client():
    """Create a test client"""
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_get_results_with_data(client):
    """Test results endpoint with sample data"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write('timestamp,meter,pv,net\n')
        f.write('2023-01-01T12:00:00,5.5,7.2,1.7\n')
        f.write('2023-01-01T12:00:03,6.1,7.1,1.0\n')
        temp_file = f.name
    
    with patch.object(config, 'RESULTS_FILE', temp_file):
        rv = client.get('/results')
        assert rv.status_code == 200
        data = rv.get_json()
        assert len(data) == 2
        assert data[0]['meter'] == 5.5
        assert data[0]['pv'] == 7.2
        assert data[0]['net'] == 1.7
    
    os.unlink(temp_file)


def test_pv_profile():
    """Test PV profile function generates bell curve"""
    # Test peak at noon
    assert pv_profile(12) > pv_profile(6)
    assert pv_profile(12) > pv_profile(18)
    
    # Test early morning and late evening are very small (near zero)
    assert pv_profile(0) < 0.1  # Very low at midnight
    assert pv_profile(24) < 0.1  # Very low at midnight (24h = 0h)
    assert pv_profile(3) < 0.1   # Very low at 3 AM
    assert pv_profile(21) < 0.1  # Very low at 9 PM
    
    # Test with minutes
    assert pv_profile(12, 0) > pv_profile(11, 30)

def test_get_status(client):
    """Test status endpoint"""
    rv = client.get('/status')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'running' in data

def test_start_simulation(client):
    """Test start simulation endpoint"""
    with patch.object(app.simulation_manager, 'start', return_value=True) as mock_start:
        rv = client.post('/start')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert data['status'] == 'started'
        assert data['running'] == True
        mock_start.assert_called_once()

def test_start_simulation_already_running(client):
    """Test start simulation when already running"""
    with patch.object(app.simulation_manager, '_running') as mock_running:
        mock_running.is_set.return_value = True
        rv = client.post('/start')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert data['status'] == 'already running'
        assert data['running'] == True

def test_stop_simulation(client):
    """Test stop simulation endpoint"""
    with patch.object(app.simulation_manager, 'stop', return_value=True) as mock_stop:
        rv = client.post('/stop')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert data['status'] == 'stopped'
        assert data['running'] == False
        mock_stop.assert_called_once()

def test_get_results_empty(client):
    """Test results endpoint when no file exists"""
    with patch('os.path.exists', return_value=False):
        rv = client.get('/results')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert data == []

def test_get_results_latest_with_data(client):
    """Test latest results endpoint with sample data"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write('timestamp,meter,pv,net\n')
        f.write('2023-01-01T12:00:00,5.5,7.2,1.7\n')
        f.write('2023-01-01T12:00:03,6.1,7.1,1.0\n')
        temp_file = f.name
    
    with patch.object(config, 'RESULTS_FILE', temp_file):
        rv = client.get('/results/latest')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert len(data) == 2
        assert data[0]['meter'] == 5.5
        assert data[0]['pv'] == 7.2
        assert data[0]['net'] == 1.7
    
    os.unlink(temp_file)

def test_get_latest_results(client):
    """Test latest results endpoint"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write('timestamp,meter,pv,net\n')
        for i in range(60):  # Create 60 entries
            meter = 5.0 + i * 0.1
            pv = 7.0 + i * 0.1
            net = pv - meter
            f.write(f'2023-01-01T12:00:{i:02d},{meter:.1f},{pv:.1f},{net:.1f}\n')
        temp_file = f.name
    
    with patch.object(config, 'RESULTS_FILE', temp_file):
        rv = client.get('/results/latest')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert len(data) == 50  # Should return only latest 50
    
    os.unlink(temp_file)

# New tests for modular components

def test_meter_reading_validation():
    """Test MeterReading model validation"""
    # Valid reading
    reading = MeterReading(timestamp=datetime.now(), meter=5.5)
    assert reading.meter == 5.5
    
    # Test rounding (Pydantic may handle rounding differently)
    reading = MeterReading(timestamp=datetime.now(), meter=5.555)
    assert reading.meter == 5.55  # Default Python rounding
    
    # Test invalid values
    with pytest.raises(ValueError):
        MeterReading(timestamp=datetime.now(), meter=-1.0)  # Negative
    
    with pytest.raises(ValueError):
        MeterReading(timestamp=datetime.now(), meter=25.0)  # Too high

def test_pv_data_validation():
    """Test PVData model validation"""
    # Valid data
    pv_data = PVData(
        timestamp=datetime.now(),
        meter=5.5,
        pv=7.2,
        net=1.7  # PV production - meter consumption
    )
    assert pv_data.meter == 5.5
    assert pv_data.pv == 7.2
    assert pv_data.net == 1.7
    
    # Test invalid PV values
    with pytest.raises(ValueError):
        PVData(timestamp=datetime.now(), meter=5.0, pv=-1.0, net=-6.0)  # Negative PV
    
    with pytest.raises(ValueError):
        PVData(timestamp=datetime.now(), meter=5.0, pv=15.0, net=10.0)  # Too high PV

def test_simulation_manager_lifecycle():
    """Test SimulationManager start/stop lifecycle"""
    manager = SimulationManager()
    
    # Initially not running
    assert not manager.is_running
    
    # Mock the connection to avoid actual RabbitMQ
    with patch('simulation.get_rabbitmq_connection') as mock_conn:
        mock_connection = Mock()
        mock_channel = Mock()
        mock_conn.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        
        # Start simulation
        success = manager.start()
        assert success
        assert manager.is_running
        
        # Try to start again (should fail)
        success = manager.start()
        assert not success  # Already running
        
        # Stop simulation
        success = manager.stop()
        assert success
        assert not manager.is_running
        
        # Try to stop again (should fail)
        success = manager.stop()
        assert not success  # Not running

def test_health_check_endpoint(client):
    """Test health check endpoint"""
    with patch('app.get_rabbitmq_connection') as mock_conn:
        mock_connection = Mock()
        mock_conn.return_value = mock_connection
        
        rv = client.get('/health')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        
        assert 'status' in data
        assert 'timestamp' in data
        assert 'services' in data
        assert 'rabbitmq' in data['services']
        assert 'filesystem' in data['services']
        assert 'simulation' in data['services']

def test_health_check_unhealthy_rabbitmq(client):
    """Test health check when RabbitMQ is down"""
    with patch('app.get_rabbitmq_connection', side_effect=Exception("Connection failed")):
        rv = client.get('/health')
        assert rv.status_code == 503
        data = json.loads(rv.data)
        assert data['status'] == 'unhealthy'
        assert data['services']['rabbitmq'] == 'unhealthy'

def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    with patch('os.path.exists', return_value=False):
        rv = client.get('/metrics')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        
        assert 'simulation_running' in data
        assert 'data_points' in data
        assert 'file_size_bytes' in data
        assert 'uptime_seconds' in data
        assert 'config' in data
        assert data['data_points'] == 0
        assert data['file_size_bytes'] == 0

def test_pv_profile_edge_cases():
    """Test PV profile function edge cases"""
    # Test exact values
    assert pv_profile(12, 0) == pv_profile(12)  # Default minute parameter
    
    # Test boundary conditions
    assert pv_profile(0) >= 0  # Should not be negative
    assert pv_profile(23) >= 0  # Should not be negative
    
    # Test maximum value at solar noon
    max_value = pv_profile(12)
    assert max_value > 0
    assert max_value <= 8  # Should not exceed 8kW

def test_config_environment_variables():
    """Test configuration reads environment variables"""
    with patch.dict(os.environ, {'METER_INTERVAL': '5', 'MAX_RESULTS_RETURNED': '100'}):
        # Import fresh config to pick up env vars
        from importlib import reload
        import config as config_module
        reload(config_module)
        
        assert config_module.config.METER_INTERVAL == 5
        assert config_module.config.MAX_RESULTS_RETURNED == 100

def test_retry_decorator():
    """Test retry decorator functionality"""
    from utils import retry_on_failure
    
    call_count = 0
    
    @retry_on_failure(max_retries=3, delay=0.1)
    def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "success"
    
    result = failing_function()
    assert result == "success"
    assert call_count == 3

def test_retry_decorator_max_failures():
    """Test retry decorator when all attempts fail"""
    from utils import retry_on_failure
    
    @retry_on_failure(max_retries=2, delay=0.1)
    def always_failing_function():
        raise Exception("Always fails")
    
    with pytest.raises(Exception):
        always_failing_function()

def test_get_status_with_uptime(client):
    """Test status endpoint includes uptime"""
    rv = client.get('/status')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    
    assert 'running' in data
    assert 'uptime' in data
    assert isinstance(data['uptime'], int)
    assert data['uptime'] >= 0

def test_csv_file_creation_with_headers():
    """Test CSV file is created with proper headers"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_file = f.name
    
    # Remove the file so we can test creation
    os.unlink(temp_file)
    
    manager = SimulationManager()
    
    with patch('simulation.get_rabbitmq_connection') as mock_conn, \
         patch.object(config, 'RESULTS_FILE', temp_file):
        
        mock_connection = Mock()
        mock_channel = Mock()
        mock_conn.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        
        # Start and quickly stop to trigger CSV creation
        manager.start()
        manager.stop()
        
        # Check that file was created with headers
        assert os.path.exists(temp_file)
        with open(temp_file, 'r') as f:
            first_line = f.readline().strip()
            assert first_line == 'timestamp,meter,pv,sum'
    
    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)
