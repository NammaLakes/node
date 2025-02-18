import pika
import json
from node.logger import ops_logger
from node.settings import CONFIG

def send_to_rabbitmq(data):
  connection = None
  try:
    ops_logger.info("Attempting to connect to RabbitMQ")
    if CONFIG["rabbitmq_user"] and CONFIG["rabbitmq_password"]:
      credentials = pika.PlainCredentials(CONFIG["rabbitmq_user"], CONFIG["rabbitmq_password"])
    else:
      credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=CONFIG["rabbitmq_host"], port=CONFIG["rabbitmq_port"], credentials=credentials))
    channel = connection.channel()
    ops_logger.info("Connected to RabbitMQ")

    ops_logger.info(f"Declaring queue: {CONFIG['rabbitmq_queue']}")
    channel.queue_declare(queue=CONFIG["rabbitmq_queue"], durable=True)

    ops_logger.info(f"Publishing data to queue: {CONFIG['rabbitmq_queue']}")
    channel.basic_publish(
      exchange='',
      routing_key=CONFIG["rabbitmq_queue"],
      body=json.dumps(data)
    )

    ops_logger.info(f"Sent data to RabbitMQ: {data}")
  except pika.exceptions.AMQPConnectionError as e:
    ops_logger.error(f"RabbitMQ connection error")
  except pika.exceptions.AMQPChannelError as e:
    ops_logger.error(f"RabbitMQ channel error")
  except Exception as e:
    ops_logger.error(f"RabbitMQ error")
  finally:
    try:
      connection.close()
      ops_logger.info("Closed RabbitMQ connection")
    except Exception as e:
      ops_logger.error(f"Error closing RabbitMQ connection: {e}")
