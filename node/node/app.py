import asyncio
import logging
from node.read import read_gpio_sensors
from node.transmit import send_to_rabbitmq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run():
    while True:
        data = await read_gpio_sensors()
        logging.info(f"Read data: {data}")
        send_to_rabbitmq(data)
        logging.info("Data sent to RabbitMQ")
        await asyncio.sleep(1)

def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
    return 0

if __name__ == "__main__":
    main()
