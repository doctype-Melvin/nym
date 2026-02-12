import sqlite3
import pandas as pd
import knime.scripting.io as knio
import uuid
from datetime import datetime

# Define the DB Path
db_path = "complyable_vault.db"

def initialize_vault():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Audit Trail (Hardened with UUID and Integrity Hash field)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_uuid TEXT UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                filepath TEXT,
                event_code TEXT,
                event_type TEXT,
                description TEXT,
                confidence_score REAL,
                details TEXT,
                integrity_hash TEXT 
            )
        ''')
        
        # Job Dictionary (Source of Truth)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_dict (
                original TEXT PRIMARY KEY,
                neutral TEXT,
                category TEXT,
                last_updated DATETIME
            )
        ''')

        # Session Summary (Certificate Data)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_summary (
                session_uuid TEXT PRIMARY KEY,
                file_name TEXT,
                pii_count INTEGER,
                neutral_count INTEGER,
                trust_score REAL,
                compliance_grade TEXT,
                processed_at DATETIME
            )
        ''')

        # Indexing for best performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_filepath ON audit_trail (filepath)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_trail (event_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_summary_session ON session_summary (session_uuid)')

        conn.commit()
        conn.close()
        return "Success", f"Vault initialized at {db_path}"
    except Exception as e:
        return "Error", str(e)

# Execute
status, message = initialize_vault()

# 3. Create Output Table for KNIME
# This provides visual confirmation in the KNIME GUI that the node executed
output_df = pd.DataFrame([{
    "Status": status,
    "Message": message,
    "Session_Run_ID": str(uuid.uuid4()), # Generates a fresh ID for this specific run
    "Initialization_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}])

knio.output_tables[0] = knio.Table.from_pandas(output_df)