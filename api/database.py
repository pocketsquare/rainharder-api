import databases
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/rainharder/rainharder.db"

database = databases.Database(DATABASE_URL)
