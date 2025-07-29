# PV Simulator Challenge

## Overview

This project simulates photovoltaic (PV) power production and household consumption, sums the values, and writes results to disk. The application includes:

- **Python backend (Flask)** for simulation and REST API
- **Angular frontend** for visualization and control  
- **RabbitMQ** as message broker
- **Docker Compose** for orchestration

## Architecture

The application follows this flow:
```
Meter → RabbitMQ → PV Simulator → CSV File → REST API → Frontend Chart
```

### Components

- **Meter**: Generates random household consumption values (0.5-10.0 kW) every 3 seconds
- **PV Simulator**: Generates bell-curve PV production values based on time of day
- **Message Broker**: RabbitMQ handles communication between meter and PV simulator
- **Backend API**: Flask REST API serves simulation data to frontend
- **Frontend**: Angular SPA with real-time chart visualization

## Features

### Backend (Python Flask)
- ✅ Random meter value generation (0.5-10.0 kW)
- ✅ Bell-curve PV simulation based on time
- ✅ RabbitMQ integration for message passing
- ✅ CSV file storage with timestamps
- ✅ REST API endpoints for simulation control
- ✅ Unit tests with pytest

### Frontend (Angular TypeScript)
- ✅ Single page application with start/stop controls
- ✅ Real-time chart visualization using Chart.js
- ✅ Status indicator (running/stopped)
- ✅ Service-based architecture for API communication
- ✅ Responsive design
- ✅ Unit tests with Jasmine/Karma

### DevOps
- ✅ Docker containers for all services
- ✅ Docker Compose orchestration
- ✅ Health checks and proper service dependencies
- ✅ Volume persistence for data
- ✅ Nginx reverse proxy for frontend

## Project Structure

```
PVSimulator/
├── backend/                 # Python Flask application
│   ├── app.py              # Main application
│   ├── test_app.py         # Unit tests
│   ├── requirements.txt    # Python dependencies
│   ├── pyproject.toml      # Python project config
│   └── Dockerfile          # Backend container
├── frontend/               # Angular application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # Angular components
│   │   │   ├── services/   # Angular services
│   │   │   └── ...
│   │   └── ...
│   ├── package.json        # Node.js dependencies
│   ├── angular.json        # Angular configuration
│   ├── Dockerfile          # Frontend container
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Service orchestration
└── README.md              # This file
```

## Quick Start Guide

### Prerequisites
- **Docker** (version 20.0 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** for cloning the repository

### Step-by-Step Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd PVSimulator
   ```

2. **Start the Application**
   ```bash
   # Build and start all services (RabbitMQ, Backend, Frontend)
   docker-compose up --build
   ```
   
   Wait for all services to start. You should see:
   - ✅ `pv-rabbitmq` - RabbitMQ message broker
   - ✅ `pv-backend` - Python Flask API
   - ✅ `pv-frontend` - Angular web application

3. **Access the Application**
   - **Main Application**: http://localhost:4200
   - **Backend API**: http://localhost:5000 (for direct API access)
   - **RabbitMQ Management**: http://localhost:15672 (username: `user`, password: `password`)

4. **Using the Application**
   - Open http://localhost:4200 in your web browser
   - Click **"Start Simulation"** to begin generating data
   - Watch the real-time chart update with meter consumption and PV production
   - Click **"Stop Simulation"** to halt data generation
   - Data is automatically saved to CSV and persists between sessions

5. **Stop the Application**
   ```bash
   # Stop all services
   docker-compose down
   
   # Stop and remove all data (complete cleanup)
   docker-compose down -v
   ```

### Troubleshooting

**If the application doesn't start:**
1. Check Docker is running: `docker --version`
2. Check Docker Compose is installed: `docker-compose --version`
3. View logs: `docker-compose logs -f`
4. Try rebuilding: `docker-compose down && docker-compose up --build --force-recreate`

**Common port conflicts:**
- If port 4200 is busy: Change frontend port in `docker-compose.yml`
- If port 5000 is busy: Change backend port in `docker-compose.yml`
- If port 5672/15672 is busy: Change RabbitMQ ports in `docker-compose.yml`

## Service Ports & Access

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| **Frontend (Angular)** | 4200 | http://localhost:4200 | Main web application interface |
| **Backend (Flask API)** | 5000 | http://localhost:5000 | REST API endpoints |
| **RabbitMQ Management** | 15672 | http://localhost:15672 | Message broker admin panel |
| **RabbitMQ AMQP** | 5672 | localhost:5672 | Message broker communication |

### Default Credentials
- **RabbitMQ**: Username: `user`, Password: `password`

## Application Features

### What the Application Does
1. **Simulates Smart Meter**: Generates random household power consumption (0.5-10.0 kW)
2. **Simulates Solar Panels**: Calculates PV production using a bell curve based on time of day
3. **Real-time Visualization**: Shows both consumption and production on a live updating chart
4. **Data Persistence**: Saves all data points to CSV file with timestamps
5. **Message Queuing**: Uses RabbitMQ for reliable communication between components

### How to Use
1. Start the application with `docker-compose up --build`
2. Open http://localhost:4200 in your browser
3. Click "Start Simulation" to begin data generation
4. Observe the real-time chart showing:
   - **Blue line**: Household power consumption (random)
   - **Orange line**: Solar panel production (time-based bell curve)
   - **Green line**: Total power (sum of both)
5. Click "Stop Simulation" to pause data generation
6. Data is automatically saved and can be restarted anytime

### Testing

#### Backend Tests
```bash
cd backend
pytest test_app.py -v
```

#### Frontend Tests
```bash
cd frontend
npm test
```

## API Endpoints

| Endpoint | Method | Description | Example Response |
|----------|--------|-------------|------------------|
| `/start` | POST | Start the simulation | `{"status": "started", "running": true}` |
| `/stop` | POST | Stop the simulation | `{"status": "stopped", "running": false}` |
| `/status` | GET | Get simulation status | `{"running": true}` |
| `/results` | GET | Get all simulation data | Array of data points |
| `/results/latest` | GET | Get latest 50 data points | Array of recent data |

## Development Setup (Optional)

If you want to run components individually for development:

#### Backend Development
```bash
cd backend
pip install -r requirements.txt
export RABBITMQ_HOST=localhost
export RABBITMQ_USER=user
export RABBITMQ_PASS=password
python app.py
```

#### Frontend Development
```bash
cd frontend/pv-simulator
npm install
ng serve
```

#### Running RabbitMQ Separately
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=user \
  -e RABBITMQ_DEFAULT_PASS=password \
  rabbitmq:3-management
```

## Usage Instructions

1. **Start the application** using Docker Compose
2. **Open the frontend** at http://localhost:4200
3. **Click "Start Simulation"** to begin data generation
4. **Watch the real-time chart** update every 2 seconds
5. **Click "Stop Simulation"** to halt data generation
6. **Data persists** in the CSV file even after stopping

## Data Format

The CSV file contains the following columns:
- `timestamp`: ISO format timestamp
- `meter`: Household consumption in kW (0.5-10.0)
- `pv`: PV production in kW (bell curve, 0-8)
- `sum`: Total power (meter + pv) in kW

## Accessing Simulation Data

### CSV File Location
The simulation data is stored in a CSV file inside the Docker container at `/app/results.csv`.

### Method 1: View Data Inside Container
```bash
# View the entire CSV file
docker exec -it pv-backend cat /app/results.csv

# View first 10 lines (including header)
docker exec -it pv-backend head -10 /app/results.csv

# View last 10 lines (most recent data)
docker exec -it pv-backend tail -10 /app/results.csv

# Follow the file in real-time as new data is added
docker exec -it pv-backend tail -f /app/results.csv

# Check file size and info
docker exec -it pv-backend ls -lh /app/results.csv

# Count total number of data rows
docker exec -it pv-backend wc -l /app/results.csv
```

### Method 2: Copy File to Host Machine
```bash
# Copy CSV file from container to your local directory
docker cp pv-backend:/app/results.csv ./simulation_data.csv

# Then view it locally
cat ./simulation_data.csv
head -10 ./simulation_data.csv
tail -10 ./simulation_data.csv
```

### Method 3: Interactive Container Access
```bash
# Get a shell inside the container
docker exec -it pv-backend /bin/bash

# Navigate and explore (you're now inside the container)
ls -la /app/
cat results.csv
tail -f results.csv  # Watch real-time data updates
exit  # Leave the container
```

### Method 4: Using API Endpoints
You can also access the data through the REST API:
```bash
# Get all simulation data
curl http://localhost:5000/results

# Get latest 50 data points
curl http://localhost:5000/results/latest

# Check simulation status
curl http://localhost:5000/status
```

### Sample CSV Data
```csv
timestamp,meter,pv,sum
2025-07-29T11:30:15.123456,5.67,3.21,8.88
2025-07-29T11:30:18.654321,4.32,3.18,7.50
2025-07-29T11:30:21.789012,6.89,3.15,10.04
```

## Technical Details

### PV Profile
The PV simulator generates a realistic bell curve with peak production at solar noon (12:00). The formula uses a Gaussian distribution:
```python
pv = max(0, 8 * exp(-((hour - 12)²) / 18))
```

### Message Flow
1. Meter thread generates random consumption values
2. Values sent to RabbitMQ queue
3. PV simulator consumes messages, calculates PV production
4. Combined data written to CSV file
5. Frontend polls API for latest data
6. Chart updates in real-time

### Docker Networking
- All services run in isolated `pv-network`
- Frontend proxies API calls to backend
- Persistent volumes for data storage
- Health checks ensure proper startup order

## Development Notes

- **Good Architecture**: Separation of concerns with services, components, and clear API boundaries
- **Testing**: Comprehensive unit tests for both backend and frontend
- **Error Handling**: Graceful error handling and user feedback
- **Responsive Design**: Mobile-friendly interface
- **Production Ready**: Docker containers with health checks and proper configurations

## Troubleshooting

### Common Issues

1. **Backend connection failed**
   - Ensure RabbitMQ is running and accessible
   - Check environment variables
   - Verify Docker network connectivity

2. **Frontend not loading data**
   - Check backend API is running on port 5000
   - Verify CORS configuration
   - Check browser developer console for errors

3. **Docker build issues**
   - Ensure Docker and Docker Compose are installed
   - Try rebuilding with `--no-cache` flag
   - Check Docker daemon is running

### Logs
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f rabbitmq
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License.
