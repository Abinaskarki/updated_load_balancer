import os
import sys
import time
import signal
import subprocess
import socket
import webbrowser

class WebDashboardDemo:
    def __init__(self):
        self.processes = []
        self.python_cmd = "/Users/abinas/Desktop/all/code/updated_load_balancer/.venv/bin/python"
        self.port = None
        self.dashboard_url = None
    
    def find_free_port(self, start_port=8080, end_port=8090):
        """Find a free port in the specified range"""
        for port in range(start_port, end_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise Exception(f"No free ports available in range {start_port}-{end_port}")
    
    def kill_processes_on_port_range(self, start_port=8080, end_port=8090):
        """Kill all processes using ports in the specified range"""
        print(f"Cleaning up ports {start_port}-{end_port}...")
        
        for port in range(start_port, end_port):
            try:
                # Find processes using the port
                result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                      capture_output=True, text=True)
                
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            try:
                                subprocess.run(['kill', '-9', pid], check=False)
                                print(f"  Killed process {pid} on port {port}")
                            except:
                                pass
            except:
                pass
    
    def cleanup_backend_ports(self):
        """Clean up backend server ports"""
        backend_ports = [3001, 3002, 3003, 3004, 3005]
        for port in backend_ports:
            try:
                result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                      capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            try:
                                subprocess.run(['kill', '-9', pid], check=False)
                                print(f"  Cleaned backend port {port}")
                            except:
                                pass
            except:
                pass
    
    def start_process(self, cmd, name):
        """Start a process and add it to the tracking list"""
        try:
            process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
            self.processes.append((process, name))
            print(f"  Started {name}")
            return process
        except Exception as e:
            print(f"  Error starting {name}: {e}")
            return None
    
    def cleanup(self, signum=None, frame=None):
        """Clean up all processes"""
        print("\nCleaning up processes...")
        for process, name in self.processes:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                print(f"   Stopped {name}")
            except:
                pass
        
        # Additional cleanup for any remaining processes
        self.kill_processes_on_port_range(8080, 8090)
        self.cleanup_backend_ports()
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
        print("WEB DASHBOARD DEMO")
        print("=" * 50)
        
        # Set up signal handler for cleanup
        signal.signal(signal.SIGINT, self.cleanup)
        
        try:
            # Step 0: Clean up any existing processes
            print("\nStep 0: Cleaning up existing processes...")
            self.kill_processes_on_port_range(8080, 8090)
            self.cleanup_backend_ports()
            time.sleep(2)  # Wait for cleanup to complete
            
            # Find available port for load balancer
            self.port = self.find_free_port(8080, 8090)
            self.dashboard_url = f"http://localhost:{self.port}"
            print(f"Using port {self.port} for load balancer")
            
            print("\nStep 1: Starting backend servers...")
            
            # Start test backend servers
            self.start_process(f"{self.python_cmd} test_server.py --port 3001", "Backend Server 1")
            time.sleep(1)
            self.start_process(f"{self.python_cmd} test_server.py --port 3002 --delay 0.1", "Backend Server 2")
            time.sleep(1)
            self.start_process(f"{self.python_cmd} test_server.py --port 3003 --delay 0.2", "Backend Server 3")
            time.sleep(2)
            
            print("Backend servers started!")
            
            print(f"\nStep 2: Starting load balancer on port {self.port}...")
            self.start_process(f"{self.python_cmd} main.py --algorithm round_robin --port {self.port}", "Load Balancer")
            
            # Wait for load balancer to start
            print("Waiting for load balancer to start...")
            if self.wait_for_server(self.dashboard_url, timeout=15):
                print("Load balancer is ready!")
            else:
                print("Warning: Load balancer may not be fully ready")
            
            print("\nStep 3: Opening web browser...")
            try:
                webbrowser.open(self.dashboard_url)
                print("Web browser opened!")
            except:
                print("Could not open browser automatically")
                print(f"Please open: {self.dashboard_url}")
            
            print("\nStep 4: Running sample load tests...")
            print("This will generate some traffic to populate the dashboard...")
            for i in range(3):
                print(f"  Running load test {i+1}/3...")
                subprocess.run(f"{self.python_cmd} load_test.py --url {self.dashboard_url} --requests 10 --concurrent 2", 
                             shell=True, capture_output=True)
                time.sleep(1)
            print("Load tests completed!")
            
            print(f"\nWEB DASHBOARD DEMO READY!")
            print("="*50)
            print(f"Dashboard URL: {self.dashboard_url}")
            
            print("\nWeb Dashboard Features:")
            print("  Real-time statistics and charts")
            print("  Server status monitoring")
            print("  Add/remove servers dynamically")
            print("  Auto-refresh controls")
            print("  Request distribution visualization")
            print("  Response time monitoring")
            print("  Error rate tracking")
            print("  Modern responsive web interface")
            
            print("\nTry these actions in the dashboard:")
            print("  1. Monitor real-time server statistics")
            print("  2. Add a new server (e.g., localhost:3004)")
            print("  3. Adjust refresh interval")
            print("  4. Run more load tests to see live updates")
            
            print("\nAdditional tests you can run:")
            print(f"  Load Test: {self.python_cmd} load_test.py --url {self.dashboard_url} --requests 50 --concurrent 5")
            print(f"  CLI Monitor: {self.python_cmd} monitor.py --url {self.dashboard_url}")
            
            print("\nPress Ctrl+C to stop all services")
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error during demo: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    demo = WebDashboardDemo()
    demo.run_demo()