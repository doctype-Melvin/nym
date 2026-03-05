import sqlite3
import pandas as pd
from pathlib import Path
import hashlib
from datetime import datetime
import os
import uuid

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
                p.label AS category,
                p.event_code, p.confidence_score
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

def toggle_pii_status(pii_id):
    #Toggles REDACT/EXCLUDE for a specific detection.
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE pending_pii 
            SET status = CASE WHEN status = 'REDACT' THEN 'EXCLUDE' ELSE 'REDACT' END
            WHERE pii_id = ?
        """, (pii_id,))
        conn.commit()

def toggle_all_pii_status(filepath, text):
    #Toggles status for ALL instances of a specific text in one file."""
    with sqlite3.connect(DB_PATH) as conn:
        # If the first one is REDACT, make them all EXCLUDE, and vice versa.
        conn.execute("""
            UPDATE pending_pii 
            SET status = CASE WHEN status = 'REDACT' THEN 'EXCLUDE' ELSE 'REDACT' END
            WHERE filepath = ? AND pii_text = ?
        """, (filepath, text))
        conn.commit()

def get_occurrence_count(filepath, text):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM pending_pii WHERE filepath = ? AND pii_text = ?", 
            (filepath, text)
        )
        count = cursor.fetchone()[0]
        return count
    
def get_pii_status(pii_id):
    with sqlite3.connect(DB_PATH) as conn:
        res = conn.execute("SELECT status FROM pending_pii WHERE pii_id = ?", (pii_id,)).fetchone()
        return res[0] if res else "REDACT"
    
def check_if_pii_exists(filepath, text):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT 1 FROM pending_pii 
            WHERE filepath = ? AND pii_text = ? 
            LIMIT 1
        """, (filepath, text))
        return cursor.fetchone() is not None
    
def update_substitution(self, row_id, substitution_text):
    query = """
    UPDATE pending_pii 
    SET substitution = ?, 
        event_code = 'USR-GIP' 
    WHERE id = ?
    """
    self.execute_query(query, (substitution_text, row_id))

def get_unsynced_count(filepath, text, target_status):
    with sqlite3.connect(DB_PATH) as conn:
        # Count how many instances ARE NOT currently set to the target_status
        res = conn.execute("""
            SELECT COUNT(DISTINCT pii_id) FROM pending_pii 
            WHERE filepath = ? AND pii_text = ? AND status != ?
        """, (filepath, text, target_status)).fetchone()
        return res[0]

def sync_all_pii_status(filepath, text, target_status):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE pending_pii SET status = ? 
            WHERE filepath = ? AND pii_text = ?
        """, (target_status, filepath, text))

def save_manual_tag(filepath, text, label, index, pii_hash):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO pending_pii (filepath, pii_text, pii_hash, label, occurrence_index, confidence_score, event_code, status, is_manual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filepath, text, pii_hash, label, index, 1.0, "USR-RED", 'REDACT', 1))
        conn.commit()

def save_neutralization(filepath, original_text, neutral_text):
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
                occurrence_index, confidence_score, event_code, status, is_manual
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filepath, original_text, hashlib.sha256(original_text.encode()).hexdigest(),
            'GEN-RE', 1, 1.0, 'USR-GIP', 'REDACT', 1
        ))
        conn.commit()

# def save_neutralization(filepath, original_text, neutral_text):
#     with sqlite3.connect(DB_PATH) as conn:
#         cursor = conn.cursor()
        
#         # 1. THE CLEANUP: Delete any GEN-FL flags that are part of this phrase
#         # This removes the "Yellow" so the "Green" can show up.
#         cursor.execute("""
#             DELETE FROM pending_pii 
#             WHERE filepath = ? 
#             AND ? LIKE '%' || pii_text || '%'
#             AND label = 'GEN-FL'
#         """, (filepath, original_text))
        
#         # 2. Update Global Dictionary (Your system "learns")
#         cursor.execute("""
#             INSERT OR REPLACE INTO job_dict (original, neutral) 
#             VALUES (?, ?)
#         """, (original_text, neutral_text))
        
#         # 3. Add the new GEN-RE record (Your "Green" highlight)
#         cursor.execute("""
#             INSERT INTO pending_pii (
#                 filepath, pii_text, pii_hash, label, 
#                 occurrence_index, confidence_score, event_code, status, is_manual
#             )
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """, (
#             filepath, original_text, hashlib.sha256(original_text.encode()).hexdigest(),
#             'GEN-RE', 1, 1.0, 'USR-GIP', 'REDACT', 1
#         ))
#         conn.commit()

def upgrade_flag_to_replacement(row_id, substitution_text):
    # Converts an AI Flag (GEN-FL) into a User Replacement (GEN-RE).
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pending_pii 
            SET label = 'GEN-RE',
                substitution = ?,
                event_code = 'USR-GIP',
                status = 'REDACT'
            WHERE id = ?
        """, (substitution_text, row_id))
        conn.commit()

def mark_as_ready(filepath, status='READY'):
    # Can toggle between database state 'ready' or 'pending'
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE pending_review SET status = ? WHERE filepath = ?",
            (status, filepath)
        )
        conn.commit()

def get_ready_for_clipboard():
    """Fetches all documents waiting in the Dashboard."""
    with sqlite3.connect(DB_PATH) as conn:
        # We return the filepath and the markdown (to generate the sanitized text)
        cursor = conn.execute(
            "SELECT filepath, markdown FROM pending_review WHERE status = 'READY'"
        )
        return cursor.fetchall()

def certify_document(filepath, original_text, sanitized_text, avg_confidence, user_id):
    # 1. Generate Metadata
    c_uuid = str(uuid.uuid4())
    hash_orig = hashlib.sha256(original_text.encode()).hexdigest()
    hash_sani = hashlib.sha256(sanitized_text.encode()).hexdigest()
    
    # 2. Map Confidence to a Compliance Grade (Example Logic)
    grade = "A" if avg_confidence > 0.9 else "B" if avg_confidence > 0.7 else "C"

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO audit_trail (
                filepath, pii_hash, label, 
                occurrence_index, confidence_score, event_code, user_id
            )
            SELECT 
                filepath, pii_hash, label, 
                occurrence_index, confidence_score, event_code, ?
            FROM pending_pii
            WHERE filepath = ?
        """, (user_id, filepath,))

        # 3. Insert into your existing final_commit table
        conn.execute("""
            INSERT INTO final_commit (
                commit_uuid, filepath, filename_sanitized, 
                hash_original, hash_sanitized, 
                approval_timestamp, user_id, compliance_grade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c_uuid, filepath, os.path.basename(filepath).replace(".pdf", "_sanitized.pdf"),
            hash_orig, hash_sani,
            datetime.now(), user_id, grade
        ))
        
        # 4. Clear the workspace for this file
        conn.execute("DELETE FROM pending_review WHERE filepath = ?", (filepath,))
        conn.execute("DELETE FROM pending_pii WHERE filepath = ?", (filepath,))
        conn.commit()

