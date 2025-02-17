import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import os

os.makedirs("logs/sensor", exist_ok=True)
os.makedirs("logs/operations", exist_ok=True)

sensor_logger = logging.getLogger("sensor_logger")
sensor_logger.setLevel(logging.INFO)
sensor_handler = TimedRotatingFileHandler("logs/sensor/sensor_data.log", when="midnight", interval=30, backupCount=1)
sensor_handler.suffix = "%Y-%m-%d"
sensor_handler.extMatch = r"^\d{4}-\d{2}-\d{2}$"
sensor_formatter = logging.Formatter("%(asctime)s - %(message)s")
sensor_handler.setFormatter(sensor_formatter)
sensor_logger.addHandler(sensor_handler)

ops_logger = logging.getLogger("ops_logger")
ops_logger.setLevel(logging.INFO)
ops_handler = RotatingFileHandler("logs/operations/operations.log", maxBytes=10*1024*1024, backupCount=4)
ops_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ops_handler.setFormatter(ops_formatter)
ops_logger.addHandler(ops_handler)
