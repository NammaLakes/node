import time
import random
from datetime import datetime
import json
from log_config import setup_logging
import math
try:
    import RPi.GPIO as GPIO
    ON_PI = True
except ImportError:
    ON_PI = False
    print("Running in simulation mode (no GPIO)")

class LakeSensor:
    def __init__(self, sensor_id, sensor_type, gpio_pin=None):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.gpio_pin = gpio_pin
        self.logger = setup_logging(f"sensor_{sensor_type}")
        
        if ON_PI and gpio_pin:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(gpio_pin, GPIO.OUT)
            
    def get_reading(self):
        """Generate realistic sensor readings based on type and time"""
        hour = datetime.now().hour
        
        if self.sensor_type == "temperature":
            # Temperature varies throughout the day (cooler at night, warmer during day)
            base = 18 + (5 * math.sin((hour - 6) * math.pi / 12))  # Peak at noon
            value = base + random.uniform(-0.5, 0.5)
            
        elif self.sensor_type == "ph":
            # pH varies slightly but stays mostly stable
            value = 7.2 + random.uniform(-0.3, 0.3)
            
        elif self.sensor_type == "dissolved_oxygen":
            # DO inversely related to temperature
            temp = 18 + (5 * math.sin((hour - 6) * math.pi / 12))
            base = 10 - (0.2 * (temp - 20))
            value = base + random.uniform(-0.5, 0.5)
            
        elif self.sensor_type == "turbidity":
            # Turbidity with occasional spikes
            value = random.uniform(2, 4)
            if random.random() < 0.05:  # 5% chance of spike
                value += random.uniform(3, 6)
                
        else:
            value = 0
            
        # Update GPIO if available
        if ON_PI and self.gpio_pin:
            if self.is_anomaly(value):
                GPIO.output(self.gpio_pin, GPIO.HIGH)  # LED on for anomaly
            else:
                GPIO.output(self.gpio_pin, GPIO.LOW)   # LED off for normal
                
        return round(value, 2)
        
    def is_anomaly(self, value):
        """Check if the reading is anomalous"""
        thresholds = {
            "temperature": (15, 25),
            "ph": (6.5, 8.5),
            "dissolved_oxygen": (6, None),
            "turbidity": (None, 5)
        }
        
        min_val, max_val = thresholds.get(self.sensor_type, (None, None))
        if min_val and value < min_val:
            return True
        if max_val and value > max_val:
            return True
        return False

class LakeMonitor:
    def __init__(self):
        self.logger = setup_logging("lake_monitor")
        
        # Initialize sensors with GPIO pins
        self.sensors = {
            "temperature": LakeSensor("temp_1", "temperature", gpio_pin=17),
            "ph": LakeSensor("ph_1", "ph", gpio_pin=18),
            "dissolved_oxygen": LakeSensor("do_1", "dissolved_oxygen", gpio_pin=27),
            "turbidity": LakeSensor("turb_1", "turbidity", gpio_pin=22)
        }
        
    def collect_data(self):
        """Collect readings from all sensors"""
        readings = {}
        anomalies = []
        
        for sensor_type, sensor in self.sensors.items():
            value = sensor.get_reading()
            readings[sensor_type] = value
            
            if sensor.is_anomaly(value):
                anomalies.append(f"🔴 {sensor_type.title()}: {value}")
        
        return readings, anomalies
    
    def run(self):
        """Main monitoring loop"""
        try:
            print("\n=== Lake Monitoring System Started ===")
            print("Press Ctrl+C to stop\n")
            
            while True:
                readings, anomalies = self.collect_data()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Clear terminal and print new readings
                print("\033[2J\033[H")  # Clear screen and move cursor to top
                print(f"=== Lake Readings at {timestamp} ===")
                print(f"Temperature: {readings['temperature']}°C")
                print(f"pH: {readings['ph']}")
                print(f"Dissolved Oxygen: {readings['dissolved_oxygen']} mg/L")
                print(f"Turbidity: {readings['turbidity']} NTU")
                
                if anomalies:
                    print("\nAnomalies Detected:")
                    for anomaly in anomalies:
                        print(anomaly)
                else:
                    print("\nAll readings normal ✅")
                
                print("\nPress Ctrl+C to stop")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            if ON_PI:
                GPIO.cleanup()

if __name__ == "__main__":
    monitor = LakeMonitor()
    monitor.run() 