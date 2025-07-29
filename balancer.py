import asyncio
import aiohttp
from aiohttp import web
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BalancingAlgorithm(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"

@dataclass
class ServerStats:
    host: str
    port: int
    active_connections: int = 0
    total_requests: int = 0
    total_errors: int = 0
    response_times: List[float] = field(default_factory=list)
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True
    
    @property
    def avg_response_time(self) -> float:
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0
    
    @property
    def error_rate(self) -> float:
        return (self.total_errors / self.total_requests) if self.total_requests > 0 else 0

class LoadBalancer:
    def __init__(self, server_file: str, algorithm: BalancingAlgorithm = BalancingAlgorithm.ROUND_ROBIN):
        with open(server_file) as f:
            servers_config = json.load(f)
        
        # Initialize server stats
        self.servers = {}
        for server in servers_config:
            key = f"{server['host']}:{server['port']}"
            self.servers[key] = ServerStats(host=server['host'], port=server['port'])
        
        self.current = 0
        self.algorithm = algorithm
        self.sessions = {}  # Session persistence: session_id -> server_key
        self.session_timeout = 3600  # 1 hour session timeout
        self._background_tasks = []  # Store background tasks
    
    def start_background_tasks(self):
        """Start background tasks - call this when event loop is running"""
        if not self._background_tasks:
            self._background_tasks.append(asyncio.create_task(self._health_check_loop()))
            self._background_tasks.append(asyncio.create_task(self._cleanup_sessions()))
    
    def get_server_key(self, server_stats: ServerStats) -> str:
        return f"{server_stats.host}:{server_stats.port}"
    
    def add_server(self, host: str, port: int):
        """Dynamic scaling: Add a new server"""
        key = f"{host}:{port}"
        if key not in self.servers:
            self.servers[key] = ServerStats(host=host, port=port)
            logger.info(f"Added new server: {key}")
    
    def remove_server(self, host: str, port: int):
        """Dynamic scaling: Remove a server"""
        key = f"{host}:{port}"
        if key in self.servers and len(self.servers) > 1:
            del self.servers[key]
            logger.info(f"Removed server: {key}")
    
    def get_next_server_round_robin(self) -> Optional[ServerStats]:
        """Round robin algorithm"""
        healthy_servers = [s for s in self.servers.values() if s.is_healthy]
        if not healthy_servers:
            return None
        
        server = healthy_servers[self.current % len(healthy_servers)]
        self.current = (self.current + 1) % len(healthy_servers)
        return server
    
    def get_next_server_least_connections(self) -> Optional[ServerStats]:
        """Least connections algorithm"""
        healthy_servers = [s for s in self.servers.values() if s.is_healthy]
        if not healthy_servers:
            return None
        
        return min(healthy_servers, key=lambda s: s.active_connections)
    
    def get_next_server(self, session_id: Optional[str] = None) -> Optional[ServerStats]:
        """Get next server based on algorithm and session persistence"""
        
        # Check for session persistence
        if session_id and session_id in self.sessions:
            server_key = self.sessions[session_id]
            if server_key in self.servers and self.servers[server_key].is_healthy:
                return self.servers[server_key]
            else:
                # Remove invalid session
                del self.sessions[session_id]
        
        # Use balancing algorithm
        if self.algorithm == BalancingAlgorithm.ROUND_ROBIN:
            server = self.get_next_server_round_robin()
        elif self.algorithm == BalancingAlgorithm.LEAST_CONNECTIONS:
            server = self.get_next_server_least_connections()
        else:
            server = self.get_next_server_round_robin()
        
        # Create session if needed
        if session_id and server:
            self.sessions[session_id] = self.get_server_key(server)
        
        return server
    
    def generate_session_id(self, request) -> str:
        """Generate session ID based on client IP and User-Agent"""
        client_ip = request.remote or "unknown"
        user_agent = request.headers.get('User-Agent', 'unknown')
        session_data = f"{client_ip}:{user_agent}:{time.time()}"
        return hashlib.md5(session_data.encode()).hexdigest()
    
    async def _health_check_loop(self):
        """Background task to check server health"""
        while True:
            for server in self.servers.values():
                try:
                    start_time = time.time()
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                        async with session.get(f"http://{server.host}:{server.port}/health") as resp:
                            response_time = time.time() - start_time
                            server.is_healthy = resp.status == 200
                            server.last_health_check = datetime.now()
                            
                            # Keep only last 100 response times
                            server.response_times.append(response_time)
                            if len(server.response_times) > 100:
                                server.response_times.pop(0)
                                
                except Exception as e:
                    server.is_healthy = False
                    server.last_health_check = datetime.now()
                    logger.warning(f"Health check failed for {server.host}:{server.port}: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def _cleanup_sessions(self):
        """Background task to cleanup expired sessions"""
        while True:
            current_time = time.time()
            expired_sessions = [
                session_id for session_id, _ in self.sessions.items()
                if current_time - float(session_id.split(':')[-1] if ':' in session_id else 0) > self.session_timeout
            ]
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
            
            await asyncio.sleep(300)  # Cleanup every 5 minutes

    async def forward_request(self, request):
        # Generate or extract session ID
        session_id = request.cookies.get('lb_session_id')
        if not session_id:
            session_id = self.generate_session_id(request)
        
        server = self.get_next_server(session_id)
        if not server:
            return web.Response(text="No healthy servers available", status=503)
        
        backend_url = f"http://{server.host}:{server.port}{request.rel_url}"
        
        # Track connection
        server.active_connections += 1
        server.total_requests += 1
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = dict(request.headers)
                # Remove hop-by-hop headers
                headers.pop('connection', None)
                headers.pop('upgrade', None)
                
                body = await request.read()
                async with session.request(
                    method=request.method,
                    url=backend_url,
                    headers=headers,
                    data=body
                ) as resp:
                    response_time = time.time() - start_time
                    server.response_times.append(response_time)
                    if len(server.response_times) > 100:
                        server.response_times.pop(0)
                    
                    response_body = await resp.read()
                    response_headers = dict(resp.headers)
                    
                    # Add session cookie
                    response = web.Response(
                        body=response_body, 
                        status=resp.status, 
                        headers=response_headers
                    )
                    response.set_cookie('lb_session_id', session_id, max_age=self.session_timeout)
                    
                    return response
                    
        except Exception as e:
            server.total_errors += 1
            logger.error(f"Backend error for {server.host}:{server.port}: {e}")
            return web.Response(text=f"Backend error: {e}", status=502)
        finally:
            server.active_connections -= 1

    async def get_stats(self, request):
        """Endpoint to get load balancer statistics"""
        stats = {
            "algorithm": self.algorithm.value,
            "total_servers": len(self.servers),
            "healthy_servers": len([s for s in self.servers.values() if s.is_healthy]),
            "active_sessions": len(self.sessions),
            "servers": {}
        }
        
        for key, server in self.servers.items():
            stats["servers"][key] = {
                "host": server.host,
                "port": server.port,
                "is_healthy": server.is_healthy,
                "active_connections": server.active_connections,
                "total_requests": server.total_requests,
                "total_errors": server.total_errors,
                "error_rate": f"{server.error_rate:.2%}",
                "avg_response_time": f"{server.avg_response_time:.3f}s",
                "last_health_check": server.last_health_check.isoformat() if server.last_health_check else None
            }
        
        return web.json_response(stats)

    async def add_server_endpoint(self, request):
        """Endpoint to dynamically add a server"""
        data = await request.json()
        host = data.get('host')
        port = data.get('port')
        
        if not host or not port:
            return web.json_response({"error": "Host and port required"}, status=400)
        
        self.add_server(host, port)
        return web.json_response({"message": f"Server {host}:{port} added successfully"})

    async def remove_server_endpoint(self, request):
        """Endpoint to dynamically remove a server"""
        data = await request.json()
        host = data.get('host')
        port = data.get('port')
        
        if not host or not port:
            return web.json_response({"error": "Host and port required"}, status=400)
        
        self.remove_server(host, port)
        return web.json_response({"message": f"Server {host}:{port} removed successfully"})

    async def dashboard(self, request):
        """Serve the monitoring dashboard"""
        try:
            with open('static/advanced_dashboard.html', 'r') as f:
                html_content = f.read()
            return web.Response(text=html_content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text="Dashboard not found", status=404)

    async def serve_static(self, request):
        """Serve static files"""
        filename = request.match_info['filename']
        try:
            with open(f'static/{filename}', 'r') as f:
                content = f.read()
            
            # Determine content type
            if filename.endswith('.css'):
                content_type = 'text/css'
            elif filename.endswith('.js'):
                content_type = 'application/javascript'
            elif filename.endswith('.html'):
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
                
            return web.Response(text=content, content_type=content_type)
        except FileNotFoundError:
            return web.Response(text="File not found", status=404)

    def get_app(self):
        app = web.Application()
        
        # Start background tasks when the app starts
        async def init_background_tasks(app):
            self.start_background_tasks()
        
        app.on_startup.append(init_background_tasks)
        
        # Dashboard endpoints (serve before catch-all route)
        app.router.add_get('/dashboard', self.dashboard)
        app.router.add_get('/', self.dashboard)  # Root serves dashboard
        app.router.add_get('/static/{filename}', self.serve_static)  # Static files
        
        # Management endpoints  
        app.router.add_get('/lb/stats', self.get_stats)
        app.router.add_post('/lb/add-server', self.add_server_endpoint)
        app.router.add_post('/lb/remove-server', self.remove_server_endpoint)
        
        # Main routing (catch-all - must be last)
        app.router.add_route('*', '/{tail:.*}', self.forward_request)
        
        return app