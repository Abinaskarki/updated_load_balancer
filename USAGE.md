# Advanced Load Balancer Usage Guide

## Quick Start

1. **Start test backend servers** (in separate terminals):

   ```bash
   python test_server.py --port 3001
   python test_server.py --port 3002 --delay 0.1
   python test_server.py --port 3003 --delay 0.2
   ```

2. **Start the load balancer**:

   ```bash
   # Round Robin (default)
   python main.py --algorithm round_robin --port 8080

   # Least Connections
   python main.py --algorithm least_connections --port 8080
   ```

3. **Access the Web Dashboard**:
   Open your browser to: `http://localhost:8080`

   Or use the automated demo:

   ```bash
   python web_demo.py
   ```

4. **Monitor via CLI** (alternative):

   ```bash
   python monitor.py --interval 3
   ```

5. **Run load tests**:
   ```bash
   python load_test.py --requests 50 --concurrent 5
   ```

##  Web Dashboard

The advanced web dashboard provides a modern, real-time monitoring interface with:

### Features

- **Real-time Statistics**: Live updating charts and metrics
- **Server Management**: Add/remove servers directly from the web interface
- **Interactive Charts**: Request distribution, response times, error rates
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Auto-refresh Controls**: Customizable refresh intervals (1s to 10s)
- **Toast Notifications**: Success/error feedback for operations
- **Connection Status**: Visual indicators for system health

### Dashboard Sections

####  System Overview

- Current load balancing algorithm
- Total and healthy server counts
- Active sessions
- Overall request/error statistics

####  Server Status

- Real-time server health indicators
- Active connection counts per server
- Request/error statistics per server
- Average response times

####  Interactive Charts

- **Request Distribution**: Doughnut chart showing load distribution
- **Response Times**: Bar chart of average response times
- **Active Connections**: Line chart of current connections
- **Error Trends**: Line chart of error rates over time

####  Management Controls

- **Monitoring Controls**: Adjust refresh intervals, pause/resume auto-refresh
- **Server Management**: Add/remove servers with immediate feedback
- **Real-time Updates**: All changes reflect immediately in the dashboard

### Keyboard Shortcuts

- `Ctrl/Cmd + R`: Manual refresh
- `Ctrl/Cmd + Space`: Toggle auto-refresh

### Access URLs

- **Main Dashboard**: `http://localhost:8080/`
- **Simple Dashboard**: `http://localhost:8080/dashboard`
- **Raw Statistics API**: `http://localhost:8080/lb/stats`

## Load Balancing Algorithms

### Round Robin

- Distributes requests evenly across all healthy servers
- Simple and fair distribution
- Good for servers with similar capacity

### Least Connections

- Routes requests to the server with the fewest active connections
- Better for servers with different capacities
- Adapts to varying request processing times

## Features

### 1. Dynamic Scaling

Add servers at runtime:

```bash
curl -X POST http://localhost:8080/lb/add-server \
  -H "Content-Type: application/json" \
  -d '{"host": "localhost", "port": 3004}'
```

Remove servers at runtime:

```bash
curl -X POST http://localhost:8080/lb/remove-server \
  -H "Content-Type: application/json" \
  -d '{"host": "localhost", "port": 3004}'
```

Using the monitor script:

```bash
python monitor.py --command add-server --host localhost --port 3004
python monitor.py --command remove-server --host localhost --port 3004
```

### 2. Session Persistence

- Automatically maintains session affinity using cookies
- Sessions are tied to specific backend servers
- Automatic session cleanup after timeout
- Session ID based on client IP and User-Agent

### 3. Health Monitoring

- Automatic health checks every 30 seconds
- Health endpoint: `/health` on each backend server
- Unhealthy servers are automatically removed from rotation
- Health status visible in statistics

### 4. Load Monitoring and Reporting

View real-time statistics:

```bash
curl http://localhost:8080/lb/stats
```

Statistics include:

- Active connections per server
- Total requests and errors
- Response times
- Error rates
- Health status
- Session count

### 5. Management API

| Endpoint            | Method | Description                  |
| ------------------- | ------ | ---------------------------- |
| `/lb/stats`         | GET    | Get load balancer statistics |
| `/lb/add-server`    | POST   | Add a new backend server     |
| `/lb/remove-server` | POST   | Remove a backend server      |

## Testing Scenarios

### Test Session Persistence

```bash
# Make requests with the same session
curl -c cookies.txt http://localhost:8080/test
curl -b cookies.txt http://localhost:8080/test
curl -b cookies.txt http://localhost:8080/test
```

### Test Different Algorithms

```bash
# Start with round robin
python main.py --algorithm round_robin &
python load_test.py --requests 20

# Stop and start with least connections
python main.py --algorithm least_connections &
python load_test.py --requests 20
```

### Test Health Monitoring

```bash
# Stop one backend server and watch the load balancer adapt
# The stopped server will be marked as unhealthy
python monitor.py --interval 2
```

### Test Dynamic Scaling

```bash
# While load testing, add/remove servers
python load_test.py --requests 100 --concurrent 10 &
python monitor.py --command add-server --host localhost --port 3005
```

## Configuration

### Server Configuration (servers.json)

```json
[
  { "host": "localhost", "port": 3001 },
  { "host": "localhost", "port": 3002 },
  { "host": "localhost", "port": 3003 }
]
```

### Command Line Options

**Load Balancer (main.py):**

- `--algorithm`: Choose balancing algorithm (round_robin, least_connections)
- `--port`: Load balancer port (default: 8080)
- `--servers`: Path to servers configuration file

**Monitor (monitor.py):**

- `--url`: Load balancer URL (default: http://localhost:8080)
- `--interval`: Monitoring refresh interval in seconds
- `--command`: Command to execute (monitor, add-server, remove-server)

**Load Tester (load_test.py):**

- `--url`: Target URL (default: http://localhost:8080)
- `--requests`: Total number of requests (default: 100)
- `--concurrent`: Concurrent requests (default: 10)

**Test Server (test_server.py):**

- `--port`: Server port (required)
- `--delay`: Artificial response delay in seconds

## Monitoring Dashboard

The monitor script provides a real-time dashboard showing:

- Current load balancing algorithm
- Server health status
- Active connections per server
- Request/error counts
- Average response times
- Session information

Example output:

```
============================================================
LOAD BALANCER STATISTICS - 2025-07-28 10:30:45
============================================================
Algorithm: round_robin
Total Servers: 3
Healthy Servers: 3
Active Sessions: 5

SERVER DETAILS:
------------------------------------------------------------
Server               Health   Connections  Requests  Errors    Avg RT
------------------------------------------------------------
localhost:3001        UP     2            45        1         0.125s
localhost:3002        UP     1            44        0         0.156s
localhost:3003        DOWN   0            43        2         0.198s
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port using `--port` parameter
2. **No healthy servers**: Check if backend servers are running and accessible
3. **Import errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)
4. **Health check failures**: Ensure backend servers have `/health` endpoint

### Debug Mode

For detailed logging, you can modify the logging level in `balancer.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about:

- Health check results
- Request routing decisions
- Session management
- Server additions/removals
