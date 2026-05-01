from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DB_PATH = str(BASE_DIR / "chroma_db_v2")
BOOKINGS_PATH = BASE_DIR / "data" / "json_files" / "bookings.json"
