"""
Configuration module for TravelGenius AI
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if it exists
load_dotenv(BASE_DIR / ".env")

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "travelgenius-default-secret-key-2025")
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    
    # Gemini API settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Database
    DATA_DIR = BASE_DIR / "data"
    DATABASE_PATH = DATA_DIR / "trips.db"
    
    # App Settings
    MAX_TRIP_DAYS = 30
    DEFAULT_CURRENCY = "INR"
    CURRENCY_SYMBOL = "₹"

# Ensure data directory exists
Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
