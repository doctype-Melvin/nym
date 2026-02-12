import sqlite3
import pandas as pd
import knime.scripting.io as knio

db_path = "complyable_vault_db"

def initialize_vault():
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    # Audit Trail Table (What/Who/Where)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_tail (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   timestamp TXT,
                   filepath TEXT,
                   event_code TEXT,
                   event_type TEXT,
                   description TEXT,
                   confidence_score REAL,
                   details TEXT 
                )
            ''')
    
    # Job Dictionary Table (Neutralizer source)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_dict (
                   original TEXT PRIMARY KEY,
                   neutral TEXT,
                   category TEXT,
                   last_updated TEXT
                   )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_summary (
                   session_id TEXT,
                   file_name TEXT,
                   pii_count INTEGER,
                   neutral_count INTEGER,
                   trust_score REAL,
                   compliancegrade TEXT,
                   processed_at TEXT
                   )
    ''')

    connect.commit()
    connect.close()

initialize_vault()

output_status = pd.DataFrame([{"db_status": "Initialized", "path": db_path}])
knio.output_tables[0] = knio.Table.from_pandas(output_status)