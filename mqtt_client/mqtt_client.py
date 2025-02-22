import asyncio
import json
import gmqtt
import logging
import sqlite3
from datetime import datetime, timezone
from jsonschema import validate, ValidationError
import sys
import os
from dotenv import load_dotenv
from contextlib import closing

# Load environment variables
load_dotenv()

# MQTT Broker Configuration
MQTT_BROKER = os.getenv("BROKER")  # Docker container name for Mosquitto broker
MQTT_PORT = os.getenv("PORT")
MQTT_TOPIC = os.getenv("TOPIC")
CLIENT_ID = "mqtt_client"

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# JSON Schema for Validation
MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "device_id": {"type": "string"},
        "sensor_type": {"type": "string"},
        "sensor_value": {"type": "number"},
        "timestamp": {"type": "string", "format": "date-time"}
    },
    "required": ["device_id", "sensor_type", "sensor_value", "timestamp"]
}

# SQLite Database Setup
DB_FILE = os.getenv("FILE")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Devices (
            device_id TEXT PRIMARY KEY,
            last_seen TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            sensor_type TEXT,
            sensor_value REAL,
            timestamp TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES Devices(device_id)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the Database
init_db()

# Create MQTT Client
client = gmqtt.Client(CLIENT_ID)

def log_invalid_message(payload, error):
    with open('invalid_messages.log', 'a') as f:
        f.write(f"{datetime.now(timezone.utc)} - Invalid Message: {payload} - Error: {error}\n")

def store_valid_message(data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Update Device Last Seen
    cursor.execute('''
        INSERT INTO Devices (device_id, last_seen)
        VALUES (?, ?)
        ON CONFLICT(device_id) DO UPDATE SET last_seen=excluded.last_seen;
    ''', (data['device_id'], data['timestamp']))
    
    # Store Event
    cursor.execute('''
        INSERT INTO Events (device_id, sensor_type, sensor_value, timestamp)
        VALUES (?, ?, ?, ?);
    ''', (data['device_id'], data['sensor_type'], data['sensor_value'], data['timestamp']))
    
    conn.commit()
    conn.close()

# Subscribe to the specified MQTT topic upon connection
def on_connect(client, flags, rc, properties):
    logging.info("Connected to MQTT Broker")
    client.subscribe(MQTT_TOPIC)

# Handle incoming MQTT messages, validate, and store them
def on_message(client, topic, payload, qos, properties):
    try:
        data = json.loads(payload)
        validate(instance=data, schema=MESSAGE_SCHEMA)
        store_valid_message(data)
        logging.info(f"Valid Data Stored: {data}")
    except (json.JSONDecodeError, ValidationError) as e:
        log_invalid_message(payload, str(e))
        logging.error(f"Invalid Message: {payload} - Error: {e}")

async def main():
    client.on_connect = on_connect
    client.on_message = on_message
    await client.connect(MQTT_BROKER, MQTT_PORT)
    while True:
        await asyncio.sleep(1)  # Keep the client running

if __name__ == "__main__":
    loop = asyncio.get_event_loop()  #get defalut event loop
    try:
        loop.run_until_complete(main())    #run the main coroutine in the event
    except KeyboardInterrupt:
        print("mqtt client stopped manually")
    finally:
        loop.close()
