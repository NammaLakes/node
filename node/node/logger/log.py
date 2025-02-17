import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import os

# Ensure log directories exist
os.makedirs("logs/sensor", exist_ok=True)
os.makedirs("logs/operations", exist_ok=True)

# Sensor Logger
sensor_logger = logging.getLogger("sensor_logger")
sensor_logger.setLevel(logging.INFO)
sensor_logger.propagate = False  # Prevent logs from propagating to the root logger

sensor_handler = TimedRotatingFileHandler(
    "logs/sensor/sensor_data.log", when="midnight", interval=30, backupCount=3
)
sensor_handler.suffix = "%Y-%m-%d"
sensor_formatter = logging.Formatter("%(asctime)s - %(message)s")
sensor_handler.setFormatter(sensor_formatter)

sensor_logger.handlers = [sensor_handler]  # Ensure no duplicate handlers

# Operations Logger
ops_logger = logging.getLogger("ops_logger")
ops_logger.setLevel(logging.INFO)
ops_logger.propagate = False

ops_handler = RotatingFileHandler(
    "logs/operations/operations.log", maxBytes=10 * 1024 * 1024, backupCount=4
)
ops_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ops_handler.setFormatter(ops_formatter)

ops_logger.handlers = [ops_handler]

# Test Logging
sensor_logger.info("Sensor logger initialized.")
ops_logger.info("Operations logger initialized.")

# Force logs to be written immediately
for handler in sensor_logger.handlers:
    handler.flush()

for handler in ops_logger.handlers:
    handler.flush()