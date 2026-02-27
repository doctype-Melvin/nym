import sqlite3
import pandas as pd
import knime.scripting.io as knio
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('./')

# Define the DB Path
db_path = os.getenv('DB_PATH', "../complyable_app/data/vault/complyable_vault.db")
csv_path = os.getenv('CSV_PATH', "../complyable_app/data/refs/dict_seed.csv")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

def initialize_vault():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Event Registry table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_registry (
                event_code TEXT PRIMARY KEY,
                category TEXT, 
                source_tier TEXT,
                methodology TEXT,
                legal_basis TEXT
            )
        """)
        # Registry events
        events = [
            ('T0-ANL', 'System', 'Tier 0', 'Tika Parser Metadata Analysis', 'System Integrity'),
            ('T1-RGX', 'Privacy', 'Tier 1', 'Deterministic REGEX Matching', 'GDPR / DSGVO'),
            ('T2-NER', 'Privacy', 'Tier 2', 'Probabilistic Named Entitiy Recognition', 'GDPR / DSVGO'),
            ('T3-GIP', 'Inclusion', 'Tier 3', 'Linguistic Gender Neutralization', 'AGG / EU AI Act'),
            ('T3-FLG', 'Inclusion', 'Tier 3', 'Morphological Gender Flagging', 'EU AI Act / D&I')
        ]
        # Populate Event Registry table 
        cursor.executemany("INSERT OR IGNORE INTO event_registry VALUES (?, ?, ?, ?, ?)", events)
        
        # Audit Trail
        # References Event Registry table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                record_uuid TEXT PRIMARY KEY,
                filepath TEXT,
                timestamp TEXT,
                event_code TEXT,
                pii_hash TEXT,
                label TEXT,
                occurrence_index INT,
                confidence_score REAL,
                integrity_hash TEXT,
                commit_uuid TEXT,
                FOREIGN KEY (event_code) REFERENCES event_registry(event_code)
                FOREIGN KEY (commit_uuid) REFERENCES final_commit(commit_uuid)
            )
        """)
        # Add index for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_filepath ON audit_trail (filepath)")

        # Pending Review (Harmonized)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_review (
                filepath TEXT PRIMARY KEY,
                original TEXT,
                markdown TEXT,
                output TEXT,
                status TEXT DEFAULT 'PENDING',
                integrity_hash TEXT
            )
        """)

        # Pending PII table for staging area
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_pii (
                pii_id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT,
                pii_text TEXT,
                pii_hash TEXT,
                label TEXT,
                occurrence_index INTEGER,
                confidence_score REAL,
                event_code TEXT,
                status TEXT DEFAULT 'REDACT', 
                is_manual INTEGER DEFAULT 0,  
                FOREIGN KEY (filepath) REFERENCES pending_review(filepath)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pending_pii_filepath ON pending_pii (filepath)")

        # Job Dictionary: Ensure columns are 'original' and 'neutral' for Tier 3
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_dict (
                original TEXT PRIMARY KEY,
                neutral TEXT,
                category TEXT
            )
        """)

        # Session Summary (Aligned with your UUID-based Writer)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_summary (
                session_uuid TEXT,
                file TEXT,
                pii_redacted INTEGER,
                gip INTEGER,
                trust_score REAL,
                compliance_grade TEXT,
                processed_at TEXT
            )
        """)

        # View for Streamlit Highlighter
        cursor.execute("""
            CREATE VIEW ui_highlight AS 
                SELECT
                p.pii_id,
                p.pii_text,
                p.filepath,
                p.pii_hash,
                COALESCE(j.neutral, p.label) AS label,
                p.occurrence_index,
                p.status,
                p.is_manual,
                p.label AS category,
                r.event_code,
                r.methodology,
                p.confidence_score
            FROM pending_pii p
            JOIN event_registry r ON p.event_code = r.event_code
            LEFT JOIN job_dict j ON p.pii_text = j.original;
        """)

        # Final Commit
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS final_commit (
                commit_uuid TEXT PRIMARY KEY,
                filepath TEXT,
                filename_sanitized TEXT,
                hash_original TEXT,
                hash_sanitized TEXT,
                approval_timestamp DATETIME,
                user_id TEXT,
                certificate_path TEXT,
                compliance_grade TEXT
            )
        """)

        # Seeding Logic for initial job title list
        cursor.execute("SELECT COUNT(*) FROM job_dict")
        if cursor.fetchone()[0] == 0:
            if os.path.exists(csv_path):
                seed_data = pd.read_csv(csv_path)
                # Ensure CSV headers match 'original', 'neutral', 'category'
                seed_data.to_sql('job_dict', conn, if_exists='append', index=False)
                print("Database seeded successfully.")
            else:
                print(f"Warning: CSV not found at {os.path.abspath(csv_path)}")

initialize_vault()

input_table = knio.input_tables[0].to_pandas()
knio.output_tables[0] = knio.Table.from_pandas(input_table)