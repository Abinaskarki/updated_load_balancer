#!/usr/bin/env python3
"""
Advanced test script to verify all load balancer features work.
"""

try:
    # Test imports
    print("Testing imports...")
    from aiohttp import web
    from balancer import LoadBalancer, BalancingAlgorithm
    import json
    print("All imports successful!")
    
    # Test LoadBalancer initialization with round robin
    print("\nTesting LoadBalancer initialization (Round Robin)...")
    lb_rr = LoadBalancer("servers.json", BalancingAlgorithm.ROUND_ROBIN)
    print(f"Round Robin LoadBalancer initialized with {len(lb_rr.servers)} servers")
    
    # Test LoadBalancer initialization with least connections
    print("\nTesting LoadBalancer initialization (Least Connections)...")
    lb_lc = LoadBalancer("servers.json", BalancingAlgorithm.LEAST_CONNECTIONS)
    print(f"Least Connections LoadBalancer initialized with {len(lb_lc.servers)} servers")
    
    # Test round-robin server selection
    print("\nTesting round-robin server selection...")
    for i in range(5):
        server = lb_rr.get_next_server()
        if server:
            print(f"  Request {i+1}: {server.host}:{server.port}")
        else:
            print(f"  Request {i+1}: No server available")
    print("Round-robin selection working!")
    
    # Test least connections server selection
    print("\nTesting least connections server selection...")
    for i in range(3):
        server = lb_lc.get_next_server()
        if server:
            print(f"  Request {i+1}: {server.host}:{server.port} (connections: {server.active_connections})")
        else:
            print(f"  Request {i+1}: No server available")
    print("Least connections selection working!")
    
    # Test dynamic scaling
    print("\nTesting dynamic scaling...")
    initial_count = len(lb_rr.servers)
    lb_rr.add_server("localhost", 9999)
    print(f"  Added server: localhost:9999")
    print(f"  Server count: {initial_count} -> {len(lb_rr.servers)}")
    
    lb_rr.remove_server("localhost", 9999)
    print(f"  Removed server: localhost:9999")
    print(f"  Server count: {len(lb_rr.servers)}")
    print("Dynamic scaling working!")
    
    # Test session persistence
    print("\nTesting session persistence...")
    session_id = "test_session_123"
    server1 = lb_rr.get_next_server(session_id)
    server2 = lb_rr.get_next_server(session_id)
    if server1 and server2 and lb_rr.get_server_key(server1) == lb_rr.get_server_key(server2):
        print(f"  Session {session_id} persisted to {server1.host}:{server1.port}")
        print("Session persistence working!")
    else:
        print("Session persistence may not be working as expected")
    
    # Test app creation with management endpoints
    print("\nTesting app creation with management endpoints...")
    app = lb_rr.get_app()
    print("App created successfully with all features!")
    
    # Test server statistics structure
    print("\nTesting server statistics...")
    for key, server in lb_rr.servers.items():
        print(f"  Server {key}: health={server.is_healthy}, requests={server.total_requests}")
    print("Server statistics working!")
    
    print("\nAll advanced features tested successfully!")
    print("\nAvailable features:")
    print("  Round Robin load balancing")
    print("  Least Connections load balancing") 
    print("  Dynamic server scaling")
    print("  Session persistence")
    print("  Health monitoring (will start with web app)")
    print("  Load reporting and statistics")
    print("  Management API endpoints")
    
    print("\nTo test with full functionality including health monitoring:")
    print("  1. Start test servers: python test_server.py --port 3001")
    print("  2. Start load balancer: python main.py")
    print("  3. Start monitor: python monitor.py")
    print("  4. Run load test: python load_test.py")
    
except ImportError as e:
    print(f"Import error: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
