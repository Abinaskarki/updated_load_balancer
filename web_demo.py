#!/usr/bin/env python3
"""
Web Dashboard Demo Script
Quick setup for demonstrating the web-based monitoring dashboard
"""

import subprocess
import time
import webbrowser
import signal
import sys
import os
from pathlib import Path

class WebDashboardDemo:
    def __init__(self):
        self.processes = []
        self.python_cmd = "/Users/abinas/Desktop/all/code/updated_load_balancer/.venv/bin/python"
        self.dashboard_url = "http://localhost:8080"
    
    def start_process(self, cmd, name):
        """Start a background process"""
        print(f"🚀 Starting {name}...")
        process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
        self.processes.append((process, name))
        return process
    
    def cleanup(self, signum=None, frame=None):
        """Clean up all processes"""
        print("\n🧹 Cleaning up processes...")
        for process, name in self.processes:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                print(f"   Stopped {name}")
            except:
                pass
        sys.exit(0)
    
    def wait_for_server(self, url, timeout=30):
        """Wait for server to become available"""
        import urllib.request
        import urllib.error
        
        for i in range(timeout):
            try:
                urllib.request.urlopen(url, timeout=1)
                return True
            except:
                time.sleep(1)
        return False
    
    def run_demo(self):
        """Run the web dashboard demo"""
        print("🌐 WEB DASHBOARD DEMO")
        print("=" * 50)
        
        # Set up signal handler for cleanup
        signal.signal(signal.SIGINT, self.cleanup)
        
        try:
            print("\n📦 Step 1: Starting backend servers...")
            
            # Start test backend servers
            self.start_process(f"{self.python_cmd} test_server.py --port 3001", "Backend Server 1")
            time.sleep(1)
            self.start_process(f"{self.python_cmd} test_server.py --port 3002 --delay 0.1", "Backend Server 2")
            time.sleep(1)
            self.start_process(f"{self.python_cmd} test_server.py --port 3003 --delay 0.2", "Backend Server 3")
            time.sleep(2)
            
            print("✅ Backend servers started!")
            
            print("\n⚖️  Step 2: Starting load balancer with web dashboard...")
            self.start_process(f"{self.python_cmd} main.py --algorithm round_robin", "Load Balancer")
            
            print("⏳ Waiting for load balancer to start...")
            if self.wait_for_server(self.dashboard_url):
                print("✅ Load balancer is ready!")
            else:
                print("❌ Failed to start load balancer")
                return
            
            print(f"\n🌐 Step 3: Opening web dashboard...")
            print(f"Dashboard URL: {self.dashboard_url}")
            
            # Open web browser
            try:
                webbrowser.open(self.dashboard_url)
                print("✅ Web browser opened!")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print(f"Please manually open: {self.dashboard_url}")
            
            print("\n🎯 Step 4: Running sample load tests...")
            print("This will generate some traffic to populate the dashboard...")
            
            # Run a few load tests to populate the dashboard
            for i in range(3):
                print(f"  Running load test {i+1}/3...")
                result = subprocess.run(
                    f"{self.python_cmd} load_test.py --requests 20 --concurrent 3", 
                    shell=True, 
                    capture_output=True
                )
                time.sleep(2)
            
            print("✅ Load tests completed!")
            
            print("\n🎉 WEB DASHBOARD DEMO READY!")
            print("=" * 50)
            print(f"Dashboard URL: {self.dashboard_url}")
            print("\nWeb Dashboard Features:")
            print("  📊 Real-time statistics and charts")
            print("  🖥️  Server status monitoring")
            print("  ➕ Add/remove servers dynamically")
            print("  🔄 Auto-refresh controls")
            print("  📈 Request distribution visualization")
            print("  ⚡ Response time monitoring")
            print("  🎯 Error rate tracking")
            print("  🌐 Modern responsive web interface")
            
            print("\nTry these actions in the dashboard:")
            print("  1. Monitor real-time server statistics")
            print("  2. Add a new server (e.g., localhost:3004)")
            print("  3. Adjust refresh interval")
            print("  4. Run more load tests to see live updates")
            
            print("\nAdditional tests you can run:")
            print(f"  Load Test: {self.python_cmd} load_test.py --requests 50 --concurrent 5")
            print(f"  CLI Monitor: {self.python_cmd} monitor.py")
            
            print("\n⌨️  Press Ctrl+C to stop all services")
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

if __name__ == "__main__":
    demo = WebDashboardDemo()
    demo.run_demo()
