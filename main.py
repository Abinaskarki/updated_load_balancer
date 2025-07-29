from aiohttp import web
from balancer import LoadBalancer, BalancingAlgorithm
import argparse

def create_app():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Advanced Load Balancer')
    parser.add_argument('--algorithm', choices=['round_robin', 'least_connections'], 
                       default='round_robin', help='Load balancing algorithm')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the load balancer on')
    parser.add_argument('--servers', default='servers.json', help='Path to servers configuration file')
    
    args = parser.parse_args()
    
    # Create load balancer with specified algorithm
    algorithm = BalancingAlgorithm.ROUND_ROBIN if args.algorithm == 'round_robin' else BalancingAlgorithm.LEAST_CONNECTIONS
    lb = LoadBalancer(args.servers, algorithm)
    
    return lb.get_app(), args.port

if __name__ == "__main__":
    app, port = create_app()
    print(f"Starting Advanced Load Balancer on port {port}")
    print("Management endpoints:")
    print(f"  - Stats: http://localhost:{port}/lb/stats")
    print(f"  - Add server: POST http://localhost:{port}/lb/add-server")
    print(f"  - Remove server: POST http://localhost:{port}/lb/remove-server")
    web.run_app(app, host="localhost", port=port)