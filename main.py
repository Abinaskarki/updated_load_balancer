from aiohttp import web
from balancer import LoadBalancer

if __name__ == "__main__":
    lb = LoadBalancer("servers.json")
    app = lb.get_app()
    web.run_app(app, host="localhost", port=8080)