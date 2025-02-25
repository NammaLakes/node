# Sensor Node Service

A Python-based sensor node service that reads GPIO sensor data and transmits it to RabbitMQ. This service is designed for continuous monitoring and data collection from hardware sensors.

## Features

- GPIO sensor data collection
- RabbitMQ integration for data transmission
- Configurable node settings
- Comprehensive logging system with rotation
  - Sensor data logs
  - Operations logs

## Prerequisites

Before running this service, ensure you have:
- Python 3.8 or higher
- Poetry (Python package manager)
- RabbitMQ server
- Access to GPIO pins (if running on hardware)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [project-directory]
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Configuration

Edit `node/settings.py` to configure:
- Node identification (`node_id`)
- Geographic location (`latitude`, `longitude`)
- RabbitMQ connection settings:
  - Host
  - Port
  - Queue name
  - Credentials

Default configuration:
```python
{
    "node_id": "belandur_01",
    "rabbitmq_host": "localhost",
    "rabbitmq_port": 5672,
    "rabbitmq_queue": "node_data"
}
```

## Running the Service

Start the service using Poetry:
```bash
poetry run start
```

The service will:
1. Initialize logging systems
2. Begin reading GPIO sensor data
3. Transmit data to RabbitMQ
4. Repeat at 1-second intervals

## Project Structure

```
node/
├── node/
│   ├── read/          # GPIO sensor reading functionality
│   ├── transmit/      # RabbitMQ transmission logic
│   ├── logger/        # Logging configuration
│   ├── settings.py    # Configuration settings
│   └── app.py         # Main application logic
└── tests/             # Test suite
```

## Logging

Logs are stored in:
- `logs/sensor/` - Sensor data logs (rotated daily)
- `logs/operations/` - Operational logs (size-based rotation)

## Testing

Run tests using:
```bash
poetry run pytest
```