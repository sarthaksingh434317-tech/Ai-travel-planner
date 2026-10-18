"""
Database module for TravelGenius AI
Provides SQLite persistence for saved travel itineraries with proper connection lifecycle.
"""
import sqlite3
import json
import uuid
import logging
from contextlib import contextmanager
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection with dict-like row access."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_session():
    """Context manager that opens and guarantees closing of the SQLite connection."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the SQLite database schema if not present."""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_trips (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                destination TEXT NOT NULL,
                starting_city TEXT,
                departure_date TEXT,
                return_date TEXT,
                duration_days INTEGER DEFAULT 1,
                travelers INTEGER DEFAULT 1,
                adults INTEGER DEFAULT 1,
                children INTEGER DEFAULT 0,
                budget_inr INTEGER DEFAULT 0,
                travel_style TEXT,
                interests TEXT,
                itinerary_json TEXT NOT NULL,
                is_sample INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_saved_trips_created ON saved_trips(created_at DESC)")
        conn.commit()
    logger.info("Database initialized successfully at %s", Config.DATABASE_PATH)

def save_trip(trip_data):
    """
    Save a generated itinerary to SQLite.
    Returns: generated trip_id (UUID string)
    """
    trip_id = trip_data.get("id") or str(uuid.uuid4())
    title = trip_data.get("title") or f"Trip to {trip_data.get('destination', 'Paradise')}"
    destination = trip_data.get("destination", "").strip()
    starting_city = trip_data.get("starting_city", "").strip()
    departure_date = trip_data.get("departure_date", "")
    return_date = trip_data.get("return_date", "")
    duration_days = int(trip_data.get("duration_days", 1))
    travelers = int(trip_data.get("travelers", 1))
    adults = int(trip_data.get("adults", 1))
    children = int(trip_data.get("children", 0))
    budget_inr = int(trip_data.get("budget_inr", 0))
    travel_style = trip_data.get("travel_style", "")
    interests = trip_data.get("interests", [])
    if isinstance(interests, list):
        interests_str = json.dumps(interests)
    else:
        interests_str = str(interests)

    itinerary_data = trip_data.get("itinerary")
    if isinstance(itinerary_data, dict):
        itinerary_json = json.dumps(itinerary_data)
    else:
        itinerary_json = str(itinerary_data or "{}")

    is_sample = 1 if trip_data.get("is_sample") else 0

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO saved_trips (
                id, title, destination, starting_city, departure_date, return_date,
                duration_days, travelers, adults, children, budget_inr,
                travel_style, interests, itinerary_json, is_sample, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            trip_id, title, destination, starting_city, departure_date, return_date,
            duration_days, travelers, adults, children, budget_inr,
            travel_style, interests_str, itinerary_json, is_sample
        ))
        conn.commit()

    return trip_id

def get_all_trips():
    """Retrieve all saved trips ordered by creation date descending."""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, destination, starting_city, departure_date, return_date,
                   duration_days, travelers, adults, children, budget_inr,
                   travel_style, interests, is_sample, created_at
            FROM saved_trips
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        trips = []
        for row in rows:
            trip = dict(row)
            try:
                trip["interests"] = json.loads(trip["interests"])
            except Exception:
                trip["interests"] = []
            trip["is_sample"] = bool(trip["is_sample"])
            trips.append(trip)
        return trips

def get_trip_by_id(trip_id):
    """Retrieve a single saved trip by ID, including its full itinerary JSON."""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM saved_trips WHERE id = ?", (trip_id,))
        row = cursor.fetchone()
        if not row:
            return None
        trip = dict(row)
        try:
            trip["interests"] = json.loads(trip["interests"])
        except Exception:
            trip["interests"] = []
        try:
            trip["itinerary"] = json.loads(trip["itinerary_json"])
        except Exception:
            trip["itinerary"] = {}
        trip["is_sample"] = bool(trip["is_sample"])
        return trip

def delete_trip(trip_id):
    """Delete a saved trip by ID. Returns True if deleted, False if not found."""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saved_trips WHERE id = ?", (trip_id,))
        conn.commit()
        return cursor.rowcount > 0
