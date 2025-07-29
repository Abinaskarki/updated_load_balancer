#!/usr/bin/env python3
"""
Load testing script for the load balancer
"""
import aiohttp
import asyncio
import time
import argparse
from statistics import mean, median

class LoadTester:
    def __init__(self, url, concurrent_requests=10, total_requests=100):
        self.url = url
        self.concurrent_requests = concurrent_requests
        self.total_requests = total_requests
        self.results = []
        self.errors = []
    
    async def make_request(self, session, request_id):
        """Make a single request and record the result"""
        start_time = time.time()
        try:
            async with session.get(f"{self.url}/test/{request_id}") as resp:
                end_time = time.time()
                response_time = end_time - start_time
                result = {
                    'request_id': request_id,
                    'status': resp.status,
                    'response_time': response_time,
                    'success': 200 <= resp.status < 300
                }
                
                if result['success']:
                    try:
                        body = await resp.json()
                        result['server_port'] = body.get('server_port', 'unknown')
                    except:
                        result['server_port'] = 'unknown'
                
                self.results.append(result)
                return result
        except Exception as e:
            end_time = time.time()
            error = {
                'request_id': request_id,
                'error': str(e),
                'response_time': end_time - start_time
            }
            self.errors.append(error)
            return error
    
    async def run_load_test(self):
        """Run the load test"""
        print(f"Starting load test: {self.total_requests} requests with {self.concurrent_requests} concurrent")
        print(f"Target URL: {self.url}")
        
        start_time = time.time()
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.concurrent_requests)
        
        async def bounded_request(session, request_id):
            async with semaphore:
                return await self.make_request(session, request_id)
        
        # Run all requests
        async with aiohttp.ClientSession() as session:
            tasks = [
                bounded_request(session, i) 
                for i in range(self.total_requests)
            ]
            await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.print_results(total_time)
    
    def print_results(self, total_time):
        """Print test results"""
        successful_requests = [r for r in self.results if r.get('success', False)]
        failed_requests = len(self.errors) + len([r for r in self.results if not r.get('success', False)])
        
        response_times = [r['response_time'] for r in successful_requests]
        
        print("\n" + "="*60)
        print("LOAD TEST RESULTS")
        print("="*60)
        
        print(f"Total Requests: {self.total_requests}")
        print(f"Successful Requests: {len(successful_requests)}")
        print(f"Failed Requests: {failed_requests}")
        print(f"Success Rate: {len(successful_requests)/self.total_requests:.2%}")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Requests per Second: {self.total_requests/total_time:.2f}")
        
        if response_times:
            print(f"\nResponse Times:")
            print(f"  Average: {mean(response_times):.3f}s")
            print(f"  Median: {median(response_times):.3f}s")
            print(f"  Min: {min(response_times):.3f}s")
            print(f"  Max: {max(response_times):.3f}s")
        
        # Server distribution
        server_distribution = {}
        for request in successful_requests:
            server = request.get('server_port', 'unknown')
            server_distribution[server] = server_distribution.get(server, 0) + 1
        
        if server_distribution:
            print(f"\nLoad Distribution:")
            for server, count in server_distribution.items():
                percentage = count / len(successful_requests) * 100
                print(f"  Server {server}: {count} requests ({percentage:.1f}%)")
        
        if self.errors:
            print(f"\nErrors:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  Request {error['request_id']}: {error['error']}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more errors")

async def main():
    parser = argparse.ArgumentParser(description='Load Balancer Load Tester')
    parser.add_argument('--url', default='http://localhost:8080', help='Load balancer URL')
    parser.add_argument('--requests', type=int, default=100, help='Total number of requests')
    parser.add_argument('--concurrent', type=int, default=10, help='Concurrent requests')
    
    args = parser.parse_args()
    
    tester = LoadTester(args.url, args.concurrent, args.requests)
    await tester.run_load_test()

if __name__ == "__main__":
    asyncio.run(main())
