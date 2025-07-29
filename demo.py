#!/usr/bin/env python3
"""
Demo script to showcase all load balancer features
Run this to see the load balancer in action!
"""

import subprocess
import time
import signal
import sys
import os
from pathlib import Path

class Demo:
    def __init__(self):
        self.processes = []
        self.python_cmd = "/Users/abinas/Desktop/all/code/updated_load_balancer/.venv/bin/python"
    
    def start_process(self, cmd, name):
        """Start a background process"""
        print(f"Starting {name}...")
        process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
        self.processes.append((process, name))
        return process
    
    def cleanup(self, signum=None, frame=None):
        """Clean up all processes"""
        print("\nCleaning up processes...")
        for process, name in self.processes:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                print(f"   Stopped {name}")
            except:
                pass
        sys.exit(0)
    
    def pause(self, message):
        """Pause execution with a message"""
        input(f"\n{message} (Press Enter to continue...)")
    
    def run_demo(self):
        """Run the complete demo"""
        print("ADVANCED LOAD BALANCER DEMO")
    
    def run_demo(self):
        """Run the complete demo"""
        print(" ADVANCED LOAD BALANCER DEMO")
        print("=" * 50)
        
        # Set up signal handler for cleanup
        signal.signal(signal.SIGINT, self.cleanup)
        
        try:
            # Step 1: Start test backend servers
            print("\n Step 1: Starting backend servers...")
            self.start_process(f"{self.python_cmd} test_server.py --port 3001", "Backend Server 1")
            time.sleep(1)
            self.start_process(f"{self.python_cmd} test_server.py --port 3002 --delay 0.1", "Backend Server 2 (slow)")
            time.sleep(1)
            self.start_process(f"{self.python_cmd} test_server.py --port 3003 --delay 0.2", "Backend Server 3 (slower)")
            time.sleep(2)
            
            self.wait_for_enter("Backend servers are running")
            
            # Step 2: Start load balancer with round robin
            print("\n  Step 2: Starting load balancer (Round Robin)...")
            lb_process = self.start_process(f"{self.python_cmd} main.py --algorithm round_robin", "Load Balancer")
            time.sleep(3)
            
            self.wait_for_enter("Load balancer is running on http://localhost:8080")
            
            # Step 3: Start monitoring
            print("\n Step 3: Starting monitoring dashboard...")
            monitor_process = self.start_process(f"{self.python_cmd} monitor.py --interval 3", "Monitor Dashboard")
            time.sleep(2)
            
            self.wait_for_enter("Monitoring dashboard is running")
            
            # Step 4: Run load test
            print("\n Step 4: Running load test...")
            subprocess.run(f"{self.python_cmd} load_test.py --requests 30 --concurrent 5", shell=True)
            
            self.wait_for_enter("Load test completed - check the monitor output")
            
            # Step 5: Test dynamic scaling
            print("\n Step 5: Testing dynamic scaling...")
            print("Adding a new server...")
            subprocess.run(f"{self.python_cmd} monitor.py --command add-server --host localhost --port 3004", shell=True)
            
            # Start the new server
            self.start_process(f"{self.python_cmd} test_server.py --port 3004", "Backend Server 4 (new)")
            time.sleep(2)
            
            self.wait_for_enter("New server added - run another load test to see the distribution")
            
            # Step 6: Another load test with more servers
            print("\n Step 6: Load test with 4 servers...")
            subprocess.run(f"{self.python_cmd} load_test.py --requests 40 --concurrent 8", shell=True)
            
            self.wait_for_enter("Second load test completed")
            
            # Step 7: Test least connections algorithm
            print("\n Step 7: Switching to Least Connections algorithm...")
            print("Stopping current load balancer...")
            
            # Stop current load balancer
            for i, (process, name) in enumerate(self.processes):
                if name == "Load Balancer":
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    self.processes.pop(i)
                    break
            
            time.sleep(2)
            
            # Start with least connections
            self.start_process(f"{self.python_cmd} main.py --algorithm least_connections", "Load Balancer (Least Connections)")
            time.sleep(3)
            
            self.wait_for_enter("Load balancer restarted with Least Connections algorithm")
            
            # Step 8: Final load test
            print("\n Step 8: Final load test with Least Connections...")
            subprocess.run(f"{self.python_cmd} load_test.py --requests 30 --concurrent 6", shell=True)
            
            self.wait_for_enter("Demo completed! Check the final statistics")
            
            # Step 9: Show final stats
            print("\n Step 9: Final statistics...")
            subprocess.run("curl -s http://localhost:8080/lb/stats | python -m json.tool", shell=True)
            
            print("\n DEMO COMPLETED!")
            print("Features demonstrated:")
            print("   Round Robin load balancing")
            print("   Least Connections load balancing")
            print("   Dynamic server scaling")
            print("   Health monitoring")
            print("   Real-time statistics")
            print("   Session persistence (automatic)")
            print("   Load testing and monitoring")
            
            self.wait_for_enter("Press Enter to clean up and exit")
            
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

if __name__ == "__main__":
    demo = Demo()
    demo.run_demo()
