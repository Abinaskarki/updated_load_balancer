# Advanced Load Balancer

An advanced asynchronous load balancer implemented in Python using aiohttp with multiple algorithms, dynamic scaling, session persistence, and a **modern web-based monitoring dashboard**.

## 🚀 Features

### Load Balancing Algorithms

- **Round Robin**: Even distribution across servers
- **Least Connections**: Routes to server with fewest active connections

### Advanced Capabilities

- **🌐 Web Dashboard**: Modern, real-time monitoring interface
- **Dynamic Scaling**: Add/remove servers at runtime
- **Session Persistence**: Sticky sessions using cookies
- **Health Monitoring**: Automatic health checks with server recovery
- **Load Reporting**: Real-time statistics and performance metrics
- **Management API**: RESTful endpoints for administration

## 📦 Quick Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Quick Demo** (recommended):

   ```bash
   python web_demo.py
   ```

   This will automatically start backend servers, the load balancer, and open the web dashboard!

3. **Manual Setup**:

   ```bash
   # Start backend servers (in separate terminals)
   python test_server.py --port 3001 &
   python test_server.py --port 3002 &
   python test_server.py --port 3003 &

   # Start load balancer
   python main.py --algorithm round_robin

   # Open browser to http://localhost:8080
   ```

## 🌐 Web Dashboard

Access the **modern web dashboard** at `http://localhost:8080` for:

- 📊 **Real-time Charts**: Request distribution, response times, error rates
- 🖥️ **Server Status**: Live server health and performance metrics
- ⚙️ **Management Controls**: Add/remove servers with one click
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🔄 **Auto-refresh**: Customizable refresh intervals (1-10 seconds)
- 🎯 **Interactive UI**: Modern interface with toast notifications

The load balancer starts on `localhost:8080` with management endpoints available.

## 🔧 Configuration

Edit `servers.json` to configure backend servers:

```json
[
  { "host": "localhost", "port": 3001 },
  { "host": "localhost", "port": 3002 },
  { "host": "localhost", "port": 3003 }
]
```

## 📊 Management API

| Endpoint            | Method | Description                    |
| ------------------- | ------ | ------------------------------ |
| `/lb/stats`         | GET    | View load balancer statistics  |
| `/lb/add-server`    | POST   | Add backend server dynamically |
| `/lb/remove-server` | POST   | Remove backend server          |

## 🧪 Testing

**Run basic functionality tests:**

```bash
python test_setup.py
```

**Load testing:**

```bash
python load_test.py --requests 100 --concurrent 10
```

**Real-time monitoring:**

```bash
python monitor.py --interval 5
```

## 📁 Project Structure

- `main.py` - Load balancer entry point with CLI options
- `balancer.py` - Advanced load balancer implementation with web dashboard
- `servers.json` - Backend server configuration
- `test_server.py` - Test backend server for demonstrations
- `monitor.py` - CLI monitoring dashboard
- `load_test.py` - Load testing utility
- `test_setup.py` - Feature verification script
- `demo.py` - Complete interactive CLI demo
- `web_demo.py` - Web dashboard demo launcher
- `static/` - Web dashboard files
  - `advanced_dashboard.html` - Modern web monitoring interface
  - `dashboard.html` - Simple web dashboard
  - `styles.css` - Additional styling
- `USAGE.md` - Comprehensive usage guide
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

## 🎬 Quick Demo

**Web Dashboard Demo** (recommended):

```bash
python web_demo.py
```

**CLI Demo**:

```bash
python demo.py
```

This will automatically:

1. Start multiple backend servers
2. Start the load balancer
3. Open the web dashboard (web_demo.py only)
4. Run monitoring
5. Execute load tests
6. Demonstrate dynamic scaling
7. Show both balancing algorithms

## 📖 Detailed Documentation

See [USAGE.md](USAGE.md) for comprehensive documentation including:

- Detailed feature explanations
- Configuration options
- Testing scenarios
- Troubleshooting guide
- API reference

## 🔍 Example Usage

```bash
# Start with least connections algorithm
python main.py --algorithm least_connections --port 8080

# Add a server dynamically
curl -X POST http://localhost:8080/lb/add-server \
  -H "Content-Type: application/json" \
  -d '{"host": "localhost", "port": 3004}'

# View statistics
curl http://localhost:8080/lb/stats

# Run load test
python load_test.py --requests 50 --concurrent 5
```
