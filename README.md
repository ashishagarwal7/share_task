# Task: MQTT Client with REST API 

This project is an MQTT client application that:
- **Subscribes** to the topic `/devices/events`.
- **Validates** incoming messages using JSON schema.
- **Stores** valid messages in a SQLite database.
- **Logs** invalid messages.
- Provides a **REST API** using FastAPI for:
  - Retrieving the latest events for a given device.
  - Listing all registered devices and their last active timestamps.

---

## Architecture Overview
This system is designed to collect, process, store, and monitor IoT device events using MQTT communication and RESTful APIs. 
It is containerized using Docker to ensure scalability and easy deployment.
This system consists of three main component:
 
1. **Mosquitto MQTT Broker**:
   - Handles the messaging between devices and the MQTT client.
2. **MQTT Client**:
   - Subscribes to '/devices/events'.
   - Validates and stores messages in a SQLite database.
3. **REST API**:
   - Built with FastAPI.
   - Exposes endpoints for real-time monitoring.

---
## Detail setup Instruction:

#Prerequisites

- install Docker
- install Docker Compose
- check docker-compose --version

After install prerequisites:
-  git clone `<repository-url>`
-  cd `<repository-directory>`
-  docker-compose up --build or docker-compose up --build -d
-  docker-compose down -v                 #To stop the all container
-  publish the data to the mosquitto broker using the below cmd:
  ```
    docker run --rm eclipse-mosquitto mosquitto_pub -h localhost -t /devices/events -m '{
    "device_id": "sensor_123", "sensor_type": "temperature", "sensor_value": 23.5, "timestamp": "2025-02-12T14:30:00Z"}'
 ```

## API Documentation:	
Check data using API: 

- GET http://localhost:8000/devices
```json
[
  {
    "device_id": "sensor",
    "last_seen": "2025-02-12T15:30:00Z"
  },
  {
    "device_id": "sensor_123",
    "last_seen": "2025-02-12T13:30:00Z"
  }
]
```

-  GET http://localhost:8000/events/{device_id}
```json
[
  {
    "event_id": 9,
    "device_id": "sensor_123",
    "sensor_type": "temperature",
    "sensor_value": 23.5,
    "timestamp": "2025-02-12T14:30:00Z"
  },
  {
    "event_id": 10,
    "device_id": "sensor_123",
    "sensor_type": "temperature",
    "sensor_value": 27.5,
    "timestamp": "2025-02-12T13:30:00Z"
  }
]
```
## Testing the Application
A. Valid Message Test
```bash
docker run --rm eclipse-mosquitto mosquitto_pub -h localhost -t /devices/events -m '{
  "device_id": "sensor_123",
  "sensor_type": "temperature",
  "sensor_value": 23.5,
  "timestamp": "2025-02-12T14:30:00Z"
}'
```
Expected Result:
- Message is processed and stored in the database.
- Logs in MQTT client container: docker logs mqtt_client

B. Invalid Message Test
```bash
docker run --rm eclipse-mosquitto mosquitto_pub -h localhost -t /devices/events -m '{
  "device_id": "sensor_123",
  "sensor_value": 23.5
}'
```
Expected Result:
- Message is logged as invalid in invalid_messages.log.
- Not stored in the database.
