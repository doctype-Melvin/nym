import sqlite3
import pandas as pd
import knime.scripting.io as knio
from datetime import datetime
import os

# Define the DB Path
db_path = "../../data/vault/complyable_vault.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

def initialize_vault():
  with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Audit Trail (The source of truth for UI highlights)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                record_uuid TEXT PRIMARY KEY,
                filepath TEXT,
                timestamp TEXT,
                event_type TEXT,
                pii_hash TEXT,
                description TEXT,
                confidence_score REAL
            )
        """)

        # 2. Pending Review (The UI's input source)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_review (
                filepath TEXT PRIMARY KEY,
                content TEXT,
                output_final TEXT,
                status TEXT DEFAULT 'PENDING'
            )
        """)

        # 3. Final Commit (The immutable archive)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS final_commit (
                filepath TEXT PRIMARY KEY,
                content_sanitized TEXT,
                approval_timestamp TEXT,
                recruiter_id TEXT,
                certificate_hash TEXT
            )
        """)

        # 4. Job Dictionary (Tier 3 Reference)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_dict (
                gendered_term TEXT PRIMARY KEY,
                neutral_term TEXT,
                morphology_rules TEXT
            )
        """)

        # 5. Session Summary
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_summary (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                files_processed INTEGER,
                errors_logged INTEGER
            )
        """)

        # 6. Column Guard: Ensure pii_hash exists if db was created earlier
        cursor.execute("PRAGMA table_info(audit_trail)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'pii_hash' not in columns:
            cursor.execute("ALTER TABLE audit_trail ADD COLUMN pii_hash TEXT")

        conn.commit()

initialize_vault()

input_table = knio.input_tables[0].to_pandas()
knio.output_tables[0] = knio.Table.from_pandas(input_table)