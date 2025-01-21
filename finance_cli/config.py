import os
from pathlib import Path

# Base directory for ledger data
LEDGER_DIR = Path.home() / ".ledger"
DATA_DIR = LEDGER_DIR / "data"
DB_FILE = DATA_DIR / "ledger.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# Ensure directories exist
LEDGER_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
