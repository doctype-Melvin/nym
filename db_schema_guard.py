import sqlite3
import pandas as pd
import knime.scripting.io as knio
from datetime import datetime
import os

# Define the DB Path
db_path = "../complyable_app/data/vault/complyable_vault.db"
csv_path = "../complyable_app/data/refs/dict_seed.csv"
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
                event_type TEXT,
                pii_hash TEXT,
                confidence_score REAL,
                integrity_hash TEXT
                FOREIGN KEY (event_code) REFERENCES event_registry(event_code)
            )
        """)

        # Pending Review (Harmonized)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_review (
                filepath TEXT PRIMARY KEY,
                content TEXT,
                output_final TEXT,
                status TEXT DEFAULT 'PENDING',
                integrity_hash TEXT
            )
        """)

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
                file_name TEXT,
                pii_count INTEGER,
                neutral_count INTEGER,
                trust_score REAL,
                compliance_grade TEXT,
                processed_at TEXT
            )
        """)

        # Final Commit
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS final_commit (
                filepath TEXT PRIMARY KEY,
                content_sanitized TEXT,
                approval_timestamp TEXT,
                recruiter_id TEXT,
                certificate_hash TEXT
            )
        """)

        # 4. Column Guards for Migration (Handling existing databases)
        # Check audit_trail
        cursor.execute("PRAGMA table_info(audit_trail)")
        audit_cols = [col[1] for col in cursor.fetchall()]
        for col_name in ['pii_hash', 'details', 'integrity_hash']:
            if col_name not in audit_cols:
                cursor.execute(f"ALTER TABLE audit_trail ADD COLUMN {col_name} TEXT")

        # Check pending_review
        cursor.execute("PRAGMA table_info(pending_review)")
        pending_cols = [col[1] for col in cursor.fetchall()]
        if 'integrity_hash' not in pending_cols:
            cursor.execute("ALTER TABLE pending_review ADD COLUMN integrity_hash TEXT")

        # 5. Seeding Logic
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