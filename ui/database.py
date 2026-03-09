import sqlite3
import pandas as pd
from pathlib import Path
import hashlib
from datetime import datetime
import os
import uuid
import re

# Path Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.getenv('DB_PATH', str(BASE_DIR / "data" / "vault" / "complyable_vault.db"))

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

        cursor.execute("""
            CREATE VIEW IF NOT EXISTS ui_highlight AS 
            SELECT
                p.pii_id, p.filepath, p.pii_text, p.pii_hash,
                COALESCE(j.neutral, p.label) AS label,
                p.occurrence_index, p.status, p.is_manual,
                p.label AS category,
                p.event_code, p.confidence_score
            FROM pending_pii p
            LEFT JOIN job_dict j ON p.pii_text = j.original
        """)
        init_users_table()
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

def get_pii_category(pii_id):
    with sqlite3.connect(DB_PATH) as conn:
        res = conn.execute(
            "SELECT label FROM pending_pii WHERE pii_id = ?",
            (pii_id,)
        ).fetchone()
        return res[0] if res else None

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

def get_pii_details(pii_id):
    with sqlite3.connect(DB_PATH) as conn:
        res = conn.execute("""
            SELECT 
                p.status,
                p.label,
                p.event_code,
                COALESCE(j.neutral, p.label) AS neutral_phrase,
                p.pii_text
            FROM pending_pii p
            LEFT JOIN job_dict j ON p.pii_text = j.original
            WHERE p.pii_id = ?
        """, (pii_id,)).fetchone()
        if res:
            return {
                "status": res[0],
                "category": res[1],
                "event_code": res[2],
                "neutral_phrase": res[3],
                "pii_text": res[4]
            }
        return None
    
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
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # 1. Update Global Dictionary
        cursor.execute("""
            INSERT OR REPLACE INTO job_dict (original, neutral) 
            VALUES (?, ?)
        """, (original_text, neutral_text))

        # 2. Check if GEN-FL rows already exist for this word in this document
        cursor.execute("""
            SELECT COUNT(*) FROM pending_pii 
            WHERE filepath = ? AND pii_text = ? AND event_code = 'T3-FLG'
        """, (filepath, original_text))
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            # Convert existing GEN-FL rows to USR-GIP in place
            cursor.execute("""
                UPDATE pending_pii 
                SET event_code = 'USR-GIP', label = ?, status = 'REDACT', is_manual = 1
                WHERE filepath = ? AND pii_text = ? AND event_code = 'T3-FLG'
            """, (neutral_text, filepath, original_text))
        else:
            # No existing rows — count occurrences and insert fresh
            cursor.execute("SELECT markdown FROM pending_review WHERE filepath = ?", (filepath,))
            row = cursor.fetchone()
            markdown = row[0] if row else ""
            matches = list(re.finditer(re.escape(original_text), markdown, re.IGNORECASE))
            matches_count = len(matches) if matches else 1

            for idx in range(1, matches_count + 1):
                cursor.execute("""
                    INSERT INTO pending_pii (
                        filepath, pii_text, pii_hash, label,
                        occurrence_index, confidence_score, event_code, status, is_manual
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    filepath, original_text,
                    hashlib.sha256(original_text.encode()).hexdigest(),
                    neutral_text, idx, 1.0, 'USR-GIP', 'REDACT', 1
                ))

        conn.commit()

def update_neutralization(filepath, original_text, old_neutral, new_neutral):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pending_pii 
            SET label = ?
            WHERE filepath = ? AND pii_text = ? 
            AND event_code IN ('USR-GIP', 'T3-GIP', 'T3-FLG')
        """, (new_neutral, filepath, original_text))
        cursor.execute(
            "DELETE FROM job_dict WHERE neutral = ?", (old_neutral,)
        )
        cursor.execute("""
            INSERT OR REPLACE INTO job_dict (original, neutral)
            VALUES (?, ?)
        """, (original_text, new_neutral))
        conn.commit()

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

def init_users_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'reviewer',
                created_at TEXT
            )
        """)
        conn.commit()

def get_user(username):
    with sqlite3.connect(DB_PATH) as conn:
        res = conn.execute(
            "SELECT user_id, username, password_hash, role FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        return res

def create_user(username, password, role='reviewer'):
    import hashlib, uuid
    user_id = str(uuid.uuid4())
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute("""
                INSERT INTO users (user_id, username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, password_hash, role, datetime.now().isoformat()))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # username already exists

def verify_user(username, password):
    import hashlib
    user = get_user(username)
    if not user:
        return None
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user[2] == password_hash:
        return {"user_id": user[0], "username": user[1], "role": user[3]}
    return None

def user_count():
    with sqlite3.connect(DB_PATH) as conn:
        res = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        return res[0]
    
def discard_document(filepath, user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pending_review 
            SET status = 'VERWORFEN' 
            WHERE filepath = ?
        """, (filepath,))
        cursor.execute("""
            INSERT OR IGNORE INTO event_registry (event_code, category, source_tier, methodology, legal_basis)
            VALUES 
                ('USR-DIS', 'USER', 'UI', 'Manual discard', 'User action'),
                ('USR-RES', 'USER', 'UI', 'Manual restore', 'User action')
        """)
        cursor.execute("""
            INSERT INTO final_commit (
                commit_uuid, filepath, filename_sanitized,
                approval_timestamp, user_id, compliance_grade
            ) VALUES (?, ?, ?, datetime('now'), ?, 'VERWORFEN')
        """, (str(uuid.uuid4()), filepath, Path(filepath).name, user_id))
        conn.commit()

def restore_document(filepath, user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pending_review 
            SET status = 'PENDING' 
            WHERE filepath = ?
        """, (filepath,))
        cursor.execute("""
            INSERT INTO final_commit (
                commit_uuid, filepath, filename_sanitized,
                approval_timestamp, user_id, compliance_grade
            ) VALUES (?, ?, ?, datetime('now'), ?, 'WIEDERHERGESTELLT')
        """, (str(uuid.uuid4()), filepath, Path(filepath).name, user_id))
        conn.commit()

def get_discarded_documents():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT filepath
            FROM pending_review 
            WHERE status = 'VERWORFEN'
            ORDER BY filepath ASC
        """, conn)

def revert_neutralization(filepath, original_text):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Revert pending_pii row back to flagged state
        cursor.execute("""
            UPDATE pending_pii
            SET event_code = 'T3-FLG',
                label = 'GEN-FL',
                is_manual = 0
            WHERE filepath = ? AND pii_text = ?
            AND event_code IN ('USR-GIP', 'T3-GIP')
        """, (filepath, original_text))
        # Remove from job_dict
        cursor.execute("""
            DELETE FROM job_dict WHERE original = ?
        """, (original_text,))
        conn.commit()