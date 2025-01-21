"""
Configuration settings for the ledger application.
"""
import os
from pathlib import Path

# Database configuration
DB_PATH = os.getenv(
    "LEDGER_DB",
    str(Path.home() / ".ledger" / "ledger.db")
)

# Ensure the database directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Database URL
DATABASE_URL = f"sqlite:///{DB_PATH}"