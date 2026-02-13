import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "intent.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS intent_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pattern TEXT NOT NULL,
  search_term TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 100,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rules_enabled_priority
ON intent_rules(enabled, priority);

CREATE TABLE IF NOT EXISTS intent_descriptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  search_term TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)
        conn.commit()
