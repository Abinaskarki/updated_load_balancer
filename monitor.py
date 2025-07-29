#!/usr/bin/env python3
"""
Load Balancer Monitoring Dashboard
"""
import aiohttp
import asyncio
import json
import time
from datetime import datetime

class LoadBalancerMonitor:
    def __init__(self, lb_url="http://localhost:8080"):
        self.lb_url = lb_url
        self.stats_url = f"{lb_url}/lb/stats"
    
    async def get_stats(self):
        """Fetch current load balancer statistics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.stats_url) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        print(f"Error fetching stats: HTTP {resp.status}")
                        return None
        except Exception as e:
            print(f"Error connecting to load balancer: {e}")
            return None
    
    def display_stats(self, stats):
        """Display statistics in a formatted way"""
        if not stats:
            print("No stats available")
            return
        
        print("\n" + "="*60)
        print(f"LOAD BALANCER STATISTICS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        print(f"Algorithm: {stats['algorithm']}")
        print(f"Total Servers: {stats['total_servers']}")
        print(f"Healthy Servers: {stats['healthy_servers']}")
        print(f"Active Sessions: {stats['active_sessions']}")
        
        print("\nSERVER DETAILS:")
        print("-" * 60)
        print(f"{'Server':<20} {'Health':<8} {'Connections':<12} {'Requests':<10} {'Errors':<8} {'Avg RT':<10}")
        print("-" * 60)
        
        for server_key, server_info in stats['servers'].items():
            health_status = "UP" if server_info['is_healthy'] else "DOWN"
            print(f"{server_key:<20} {health_status:<8} {server_info['active_connections']:<12} "
                  f"{server_info['total_requests']:<10} {server_info['total_errors']:<8} "
                  f"{server_info['avg_response_time']:<10}")
    
    async def add_server(self, host, port):
        """Add a new server to the load balancer"""
        add_url = f"{self.lb_url}/lb/add-server"
        data = {"host": host, "port": port}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(add_url, json=data) as resp:
                    result = await resp.json()
                    print(f"Add server result: {result}")
                    return resp.status == 200
        except Exception as e:
            print(f"Error adding server: {e}")
            return False
    
    async def remove_server(self, host, port):
        """Remove a server from the load balancer"""
        remove_url = f"{self.lb_url}/lb/remove-server"
        data = {"host": host, "port": port}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(remove_url, json=data) as resp:
                    result = await resp.json()
                    print(f"Remove server result: {result}")
                    return resp.status == 200
        except Exception as e:
            print(f"Error removing server: {e}")
            return False
    
    async def monitor_loop(self, interval=5):
        """Continuous monitoring loop"""
        print("Starting Load Balancer Monitor...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                stats = await self.get_stats()
                self.display_stats(stats)
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Load Balancer Monitor')
    parser.add_argument('--url', default='http://localhost:8080', help='Load balancer URL')
    parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in seconds')
    parser.add_argument('--command', choices=['monitor', 'add-server', 'remove-server'], 
                       default='monitor', help='Command to execute')
    parser.add_argument('--host', help='Server host (for add/remove commands)')
    parser.add_argument('--port', type=int, help='Server port (for add/remove commands)')
    
    args = parser.parse_args()
    
    monitor = LoadBalancerMonitor(args.url)
    
    if args.command == 'monitor':
        await monitor.monitor_loop(args.interval)
    elif args.command == 'add-server':
        if not args.host or not args.port:
            print("Host and port required for add-server command")
            return
        await monitor.add_server(args.host, args.port)
    elif args.command == 'remove-server':
        if not args.host or not args.port:
            print("Host and port required for remove-server command")
            return
        await monitor.remove_server(args.host, args.port)

if __name__ == "__main__":
    asyncio.run(main())
