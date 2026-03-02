import sqlite3
import pandas as pd
from pathlib import Path
import hashlib

# Path Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "vault" / "complyable_vault.db"

def init_db_schema():
    #Initializes the SQLite database, tables, and the UI View
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_pii (
                pii_id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT, pii_text TEXT, pii_hash TEXT,
                label TEXT, occurrence_index INTEGER,
                confidence_score REAL, event_code TEXT,
                status TEXT DEFAULT 'REDACT', is_manual INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_review (
                filepath TEXT PRIMARY KEY, original TEXT,
                markdown TEXT, output TEXT,
                status TEXT DEFAULT 'PENDING', integrity_hash TEXT
            )
        """)
        cursor.execute("CREATE TABLE IF NOT EXISTS job_dict (original TEXT PRIMARY KEY, neutral TEXT)")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_registry (
                event_code TEXT PRIMARY KEY, category TEXT, 
                source_tier TEXT, methodology TEXT, legal_basis TEXT
            )
        """)
        cursor.execute("DROP VIEW IF EXISTS ui_highlight")
        cursor.execute("""
            CREATE VIEW ui_highlight AS 
            SELECT
                p.pii_id, p.filepath, p.pii_text, p.pii_hash,
                COALESCE(j.neutral, p.label) AS label,
                p.occurrence_index, p.status, p.is_manual,
                p.label AS category, p.confidence_score
            FROM pending_pii p
            LEFT JOIN job_dict j ON p.pii_text = j.original
        """)
        conn.commit()

def get_pending_data():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT filepath, markdown FROM pending_review WHERE status = 'PENDING'", conn)

def get_detected_data(filepath):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM ui_highlight WHERE filepath = ?", conn, params=(filepath,))

def update_pii_status(pii_id):
    #Toggles REDACT/EXCLUDE for a specific detection.
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE pending_pii 
            SET status = CASE WHEN status = 'REDACT' THEN 'EXCLUDE' ELSE 'REDACT' END
            WHERE pii_id = ?
        """, (pii_id,))
        conn.commit()

def save_manual_tag(filepath, text, label, index, pii_hash):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO pending_pii (filepath, pii_text, pii_hash, label, occurrence_index, confidence_score, event_code, status, is_manual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filepath, text, pii_hash, label, index, 1.0, "USER-UI", 'REDACT', 1))
        conn.commit()

def save_neutral(filepath, original_text, neutral_text):
    #Saves a neutral phrase to the global dict and marks it in the current file
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 1. Update Global Dictionary (for future hits)
        cursor.execute("""
            INSERT OR REPLACE INTO job_dict (original, neutral) 
            VALUES (?, ?)
        """, (original_text, neutral_text))
        
        # 2. Add to Pending PII (to trigger the UI highlight now)
        cursor.execute("""
            INSERT INTO pending_pii (
                filepath, pii_text, pii_hash, label, 
                occurrence_index, confidence_score, event_code, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filepath, original_text, hashlib.sha256(original_text.encode()).hexdigest(),
            'GEN-RE', 1, 1.0, 'T3-GIP', 'REDACT'
        ))
        conn.commit()