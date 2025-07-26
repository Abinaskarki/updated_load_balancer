# Load Balancer

An Updated asynchronous load balancer implemented in Python using aiohttp.

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure backend servers:**
   Edit `servers.json` to specify your backend servers:

   ```json
   [
     { "host": "localhost", "port": 3001 },
     { "host": "localhost", "port": 3002 },
     { "host": "localhost", "port": 3003 }
   ]
   ```

3. **Run the load balancer:**
   ```bash
   python main.py
   ```

The load balancer will start on `localhost:8080` and distribute requests across the configured backend servers using round-robin algorithm.

## Testing

Run the test script to verify everything is working:

```bash
python test_setup.py
```

## Project Structure

- `main.py` - Entry point that starts the load balancer
- `balancer.py` - Load balancer implementation
- `servers.json` - Backend server configuration
- `requirements.txt` - Python dependencies
- `test_setup.py` - Test script to verify setup
