import zmq
import json
import threading
import time
import random
import math
from datetime import datetime
from log_config import setup_logging

class LakeSensor:
    def __init__(self, sensor_id, sensor_type):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        
    def get_reading(self):
        """Generate sensor readings based on type"""
        readings = {
            "temperature": random.uniform(15, 30),      # Celsius
            "ph": random.uniform(6.0, 9.0),            # pH scale
            "dissolved_oxygen": random.uniform(6, 12),  # mg/L
            "turbidity": random.uniform(1, 10),        # NTU
            "conductivity": random.uniform(100, 500)    # µS/cm
        }
        return round(readings[self.sensor_type], 2)

class LakeNode:
    def __init__(self, lake_id, total_lakes):
        self.logger = setup_logging(f"lake_node_{lake_id}")
        self.lake_id = lake_id
        self.total_lakes = total_lakes
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = 5555 + lake_id
        self.socket.bind(f"tcp://*:{self.port}")
        self.logger.info(f"Lake node {lake_id} started on port {self.port}")
        
        # Initialize sensors
        self.sensors = [
            LakeSensor(f"lake{lake_id}_temp", "temperature"),
            LakeSensor(f"lake{lake_id}_ph", "ph"),
            LakeSensor(f"lake{lake_id}_oxygen", "dissolved_oxygen"),
            LakeSensor(f"lake{lake_id}_turbidity", "turbidity"),
            LakeSensor(f"lake{lake_id}_conductivity", "conductivity")
        ]
        
    def generate_mock_data(self):
        """Generate mock sensor data with deliberate anomalies for testing"""
        # Get current time for time-based scenarios
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        second = current_time.second
        
        # Create different scenarios based on lake_id
        if self.lake_id == 0:
            # Lake 0: Temperature spike every 30 seconds
            if second < 30:
                temp = 26.5  # High temperature anomaly
                status = 'warning'
            else:
                temp = 20.5  # Normal temperature
                status = 'normal'
            
            return {
                'lake_id': self.lake_id,
                'temperature': temp,
                'ph': 7.2,
                'dissolved_oxygen': 8.5,
                'turbidity': 3.0,
                'timestamp': current_time.isoformat(),
                'status': status
            }
            
        elif self.lake_id == 1:
            # Lake 1: Low pH and DO problems
            return {
                'lake_id': self.lake_id,
                'temperature': 22.0,
                'ph': 6.2,  # Low pH anomaly
                'dissolved_oxygen': 5.8,  # Low DO anomaly
                'turbidity': 4.0,
                'timestamp': current_time.isoformat(),
                'status': 'warning'
            }
            
        elif self.lake_id == 2:
            # Lake 2: Turbidity spikes every minute
            if minute % 2 == 0:
                turbidity = 7.5  # High turbidity anomaly
                status = 'warning'
            else:
                turbidity = 3.5
                status = 'normal'
                
            return {
                'lake_id': self.lake_id,
                'temperature': 21.0,
                'ph': 7.5,
                'dissolved_oxygen': 8.0,
                'turbidity': turbidity,
                'timestamp': current_time.isoformat(),
                'status': status
            }
            
        else:
            # Default lake: Normal readings
            return {
                'lake_id': self.lake_id,
                'temperature': 20.0,
                'ph': 7.4,
                'dissolved_oxygen': 9.0,
                'turbidity': 2.5,
                'timestamp': current_time.isoformat(),
                'status': 'normal'
            }

    def run(self):
        """Run the lake node and publish sensor data"""
        self.logger.info(f"Lake {self.lake_id} starting data transmission")
        while True:
            try:
                data = self.generate_mock_data()
                message = f"lake_{self.lake_id} {str(data)}"
                self.socket.send_string(message)
                
                # Log with different levels based on status
                if data['status'] == 'normal':
                    self.logger.debug(f"Lake {self.lake_id} readings: {data}")
                else:
                    self.logger.warning(f"Lake {self.lake_id} abnormal readings: {data}")
                    
                time.sleep(1)  # Send data every second
                
            except Exception as e:
                self.logger.error(f"Error in lake node {self.lake_id}: {e}")
                break

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python lake_node.py <lake_id> <total_lakes>")
        sys.exit(1)
        
    lake_id = int(sys.argv[1])
    total_lakes = int(sys.argv[2])
    node = LakeNode(lake_id, total_lakes)
    node.run()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down lake node...") 