import subprocess
import time
from log_config import setup_logging
import signal
import sys
import os

logger = setup_logging("test_system")

def cleanup_processes(processes):
    """Cleanup all running processes"""
    logger.info("Cleaning up processes...")
    for process in processes:
        if process.poll() is None:  # If process is still running
            try:
                process.terminate()
                process.wait(timeout=2)  # Wait for up to 2 seconds
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if it doesn't terminate
            logger.info(f"Process {process.pid} terminated")

def run_test():
    processes = []
    try:
        # Start the main zeromq script with automated input
        logger.info("Starting system test...")
        
        # Start collector first
        collector = subprocess.Popen([sys.executable, 'lake_dashboard.py'])
        processes.append(collector)
        logger.info("Started collector process")
        
        # Wait for collector to initialize
        time.sleep(2)
        
        # Start 3 lake nodes for testing
        num_lakes = 3
        for lake_id in range(num_lakes):
            node = subprocess.Popen([
                sys.executable, 
                'lake_node.py', 
                str(lake_id), 
                str(num_lakes)
            ])
            processes.append(node)
            logger.info(f"Started lake node {lake_id}")
        
        # Let the system run for 30 seconds
        logger.info("System running... waiting 30 seconds")
        time.sleep(30)
        
        # Check if all processes are still running
        all_running = all(p.poll() is None for p in processes)
        if all_running:
            logger.info("Test successful: All processes running correctly")
        else:
            logger.error("Test failed: Some processes have terminated")
            
        # Check if log files were created
        log_files = list(os.path.join('logs', f) for f in os.listdir('logs') if f.endswith('.log'))
        logger.info(f"Log files created: {log_files}")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise
    finally:
        cleanup_processes(processes)
        logger.info("Test completed")

if __name__ == "__main__":
    run_test() 