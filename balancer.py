import asyncio
import aiohttp
from aiohttp import web
import json

class LoadBalancer:
    def __init__(self, server_file):
        with open(server_file) as f:
            self.servers = json.load(f)
        self.current = 0
        self.total = len(self.servers)

    def get_next_server(self):
        server = self.servers[self.current]
        self.current = (self.current + 1) % self.total
        return server

    async def forward_request(self, request):
        server = self.get_next_server()
        backend_url = f"http://{server['host']}:{server['port']}{request.rel_url}"
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = dict(request.headers)
                body = await request.read()
                async with session.request(
                    method=request.method,
                    url=backend_url,
                    headers=headers,
                    data=body
                ) as resp:
                    response_body = await resp.read()
                    return web.Response(body=response_body, status=resp.status, headers=resp.headers)
        except Exception as e:
            return web.Response(text=f"Backend error: {e}", status=502)

    def get_app(self):
        app = web.Application()
        app.router.add_route('*', '/{tail:.*}', self.forward_request)
        return app