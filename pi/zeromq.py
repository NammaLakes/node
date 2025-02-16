# This file will serve as our main initialization script
import zmq
import threading
import os
import sys
import subprocess
import time
from log_config import setup_logging

# Initialize logger
logger = setup_logging("zeromq")

def start_collector():
    """Start the data collector process"""
    try:
        subprocess.Popen([sys.executable, 'lake_dashboard.py'])
        logger.info("Data collector process started successfully")
    except Exception as e:
        logger.error(f"Failed to start data collector: {e}")
        raise

def start_lake_nodes(num_lakes):
    """Start multiple lake node processes"""
    for lake_id in range(num_lakes):
        try:
            subprocess.Popen([sys.executable, 'lake_node.py', str(lake_id), str(num_lakes)])
            logger.info(f"Started lake node {lake_id}")
        except Exception as e:
            logger.error(f"Failed to start lake node {lake_id}: {e}")
            raise

def main():
    logger.info("Starting Lake Monitoring System")
    
    # Ensure all required files exist
    required_files = ['lake_node.py', 'lake_dashboard.py']
    for file in required_files:
        if not os.path.exists(file):
            logger.error(f"Required file {file} not found!")
            return

    try:
        num_lakes = int(input("Enter the number of lakes to monitor: "))
        logger.info(f"Configuring system for {num_lakes} lakes")
    except ValueError:
        logger.error("Invalid input: Please enter a valid number")
        return
    
    logger.info("Starting Data Collector...")
    start_collector()
    
    # Give collector time to start up
    time.sleep(2)
    
    logger.info(f"Starting {num_lakes} lake nodes...")
    start_lake_nodes(num_lakes)
    
    logger.info("Sensor network started! Data is being collected.")
    logger.info("Press Ctrl+C to shut down the system.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        logger.info("Shutting down the system...")

if __name__ == "__main__":
    main()