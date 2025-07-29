import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
import app

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client

def test_pv_profile():
    """Test PV profile function generates bell curve"""
    # Test peak at noon
    assert app.pv_profile(12) > app.pv_profile(6)
    assert app.pv_profile(12) > app.pv_profile(18)
    
    # Test early morning and late evening are very small (near zero)
    assert app.pv_profile(0) < 0.1  # Very low at midnight
    assert app.pv_profile(24) < 0.1  # Very low at midnight (24h = 0h)
    assert app.pv_profile(3) < 0.1   # Very low at 3 AM
    assert app.pv_profile(21) < 0.1  # Very low at 9 PM
    
    # Test with minutes
    assert app.pv_profile(12, 0) > app.pv_profile(11, 30)

def test_get_status(client):
    """Test status endpoint"""
    rv = client.get('/status')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'running' in data

def test_start_simulation(client):
    """Test start simulation endpoint"""
    with patch('app.threading.Thread') as mock_thread:
        rv = client.post('/start')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert data['status'] == 'started' or data['status'] == 'already running'
        assert 'running' in data

def test_stop_simulation(client):
    """Test stop simulation endpoint"""
    rv = client.post('/stop')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['status'] == 'stopped'
    assert data['running'] == False

def test_get_results_empty(client):
    """Test results endpoint when no file exists"""
    with patch('os.path.exists', return_value=False):
        rv = client.get('/results')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert data == []

def test_get_results_with_data(client):
    """Test results endpoint with sample data"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write('timestamp,meter,pv,sum\n')
        f.write('2023-01-01T12:00:00,5.5,7.2,12.7\n')
        f.write('2023-01-01T12:00:03,6.1,7.1,13.2\n')
        temp_file = f.name
    
    with patch('app.RESULTS_FILE', temp_file):
        rv = client.get('/results')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert len(data) == 2
        assert data[0]['meter'] == 5.5
        assert data[0]['pv'] == 7.2
        assert data[0]['sum'] == 12.7
    
    os.unlink(temp_file)

def test_get_latest_results(client):
    """Test latest results endpoint"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write('timestamp,meter,pv,sum\n')
        for i in range(60):  # Create 60 entries
            f.write(f'2023-01-01T12:00:{i:02d},5.{i},7.{i},12.{i}\n')
        temp_file = f.name
    
    with patch('app.RESULTS_FILE', temp_file):
        rv = client.get('/results/latest')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert len(data) == 50  # Should return only latest 50
    
    os.unlink(temp_file)
