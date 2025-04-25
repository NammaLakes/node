import random
import asyncio
import json
import time
from node.logger import sensor_logger
from node.settings import CONFIG


# The below function is just for testing and passing random values
async def read_gpio_sensors():
    # Simulate reading a sensor
    temp = random.uniform(20, 100)
    ph = random.uniform(6.5, 8.5)
    data = {
        "node_id": CONFIG["node_id"],
        # "latitude": CONFIG["latitude"],
        # "longitude": CONFIG["longitude"],
        # "temperature": temp,
        # "ph": ph
        "timestamp": time.time(),
        "payload": {"temperature": temp, "ph": ph},
    }

    sensor_logger.info(json.dumps(data))
    return data
