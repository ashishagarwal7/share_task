import os
import logging
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv, dotenv_values

# Load environment variables
load_dotenv()

#DB_FILE = "/app/events.db"
DB_FILE=os.getenv("FILE")

# Configure logging
logging.basicConfig(
    filename="app.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

class Event(BaseModel):
    event_id: int
    device_id: str
    sensor_type: str
    sensor_value: float
    timestamp: str

#connection with database
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

#Fetch all registered devices along with their last seen timestamps
@app.get("/devices", tags=["Devices"])
def get_devices(db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT device_id, last_seen FROM Devices")
        devices = cursor.fetchall()
        return [{"device_id": d["device_id"], "last_seen": d["last_seen"]} for d in devices]
    except sqlite3.Error as e:
        logging.error(f"Error fetching devices: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving devices")
    finally:
        db.close()

#Retrieve all events for a given device, ordered by timestamp.
@app.get("/events/{device_id}", response_model=List[Event], tags=["Events"])
def get_device_events(device_id: str, db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT event_id, device_id, sensor_type, sensor_value, timestamp 
            FROM Events WHERE device_id=? ORDER BY timestamp DESC
        """, (device_id,))
        events = cursor.fetchall()
        if not events:
            raise HTTPException(status_code=404, detail="No events found for this device")
        return [Event(event_id=e["event_id"], device_id=e["device_id"], sensor_type=e["sensor_type"], sensor_value=e["sensor_value"], timestamp=e["timestamp"]) for e in events]
    except sqlite3.Error as e:
        logging.error(f"Error fetching events for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving events")
    finally:
        db.close()

