#!/usr/bin/env python3
"""
Simple test backend server for load balancer testing
"""
from aiohttp import web
import argparse
import asyncio
import json

class TestServer:
    def __init__(self, port, delay=0):
        self.port = port
        self.delay = delay
        self.request_count = 0
    
    async def handle_request(self, request):
        self.request_count += 1
        
        # Simulate processing delay
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        response_data = {
            "server_port": self.port,
            "request_count": self.request_count,
            "path": str(request.rel_url),
            "method": request.method,
            "message": f"Hello from server on port {self.port}!"
        }
        
        return web.json_response(response_data)
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "port": self.port,
            "request_count": self.request_count
        })
    
    def create_app(self):
        app = web.Application()
        app.router.add_get('/health', self.health_check)
        app.router.add_route('*', '/{tail:.*}', self.handle_request)
        return app

def main():
    parser = argparse.ArgumentParser(description='Test Backend Server')
    parser.add_argument('--port', type=int, required=True, help='Port to run the server on')
    parser.add_argument('--delay', type=float, default=0, help='Artificial delay in seconds')
    
    args = parser.parse_args()
    
    server = TestServer(args.port, args.delay)
    app = server.create_app()
    
    print(f"Starting test server on port {args.port} (delay: {args.delay}s)")
    web.run_app(app, host="localhost", port=args.port)

if __name__ == "__main__":
    main()
