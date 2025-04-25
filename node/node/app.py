import asyncio
import logging
import threading
from node.read import read_gpio_sensors
from node.transmit import send_to_rabbitmq
from node.settings import CONFIG

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def run():
    while True:
        data = await read_gpio_sensors()
        logging.info(f"Read data: {data}")
        send_to_rabbitmq(data)
        logging.info("Data sent to RabbitMQ")
        await asyncio.sleep(1)


def main():
    try:
        # Start GUI in a separate thread if enabled
        if CONFIG.get("gui_enabled", False):
            from node.ui.gui import start_gui

            gui_thread = threading.Thread(target=start_gui, daemon=True)
            gui_thread.start()
            logging.info("GUI started in background")

        # Run the main application loop
        asyncio.run(run())
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
    return 0


if __name__ == "__main__":
    main()
