import asyncio
from node.read import read_gpio_sensors
from node.transmit import send_to_rabbitmq

async def run():
    while True:
        data = await read_gpio_sensors()
        send_to_rabbitmq(data)
        await asyncio.sleep(10)

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
