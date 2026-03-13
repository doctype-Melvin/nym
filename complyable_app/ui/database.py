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
CSV_PATH = str(BASE_DIR / "data" / "refs" / "dict_seed.csv")

def init_db_schema():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # ── Core tables ───────────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_registry (
                event_code TEXT PRIMARY KEY,
                category TEXT,
                source_tier TEXT,
                methodology TEXT,
                legal_basis TEXT
            )
        """)
        cursor.executemany("INSERT OR IGNORE INTO event_registry VALUES (?, ?, ?, ?, ?)", [
            ('T0-DOC', 'System',    'Tier 0', 'Docling Document Parse & Metadata Extraction', 'System Integrity'),
            ('T1-RGX', 'Privacy',   'Tier 1', 'Deterministic REGEX Matching',                 'GDPR / DSGVO'),
            ('T2-NER', 'Privacy',   'Tier 2', 'Probabilistic Named Entity Recognition',       'GDPR / DSGVO'),
            ('T3-GIP', 'Inclusion', 'Tier 3', 'Linguistic Gender Neutralization',             'AGG / EU AI Act'),
            ('T3-FLG', 'Inclusion', 'Tier 3', 'Morphological Gender Flagging',                'EU AI Act / D&I'),
            ('USR-RED', 'Privacy',  'User',   'Manual Redaction/Labeling',                   'GDPR / DSGVO / Data Minimization'),
            ('USR-GIP', 'Inclusion','User',   'Manual Gender Neutralization',                 'AGG / EU AI Act'),
            ('USR-DIS', 'System',   'User',   'Document Discarded by User',                   'User Action'),
            ('USR-RES', 'System',   'User',   'Document Restored by User',                    'User Action'),
        ])

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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_dict (
                original TEXT PRIMARY KEY,
                neutral TEXT,
                category TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS final_commit (
                commit_uuid TEXT PRIMARY KEY,
                audit_id TEXT,
                filename_hash TEXT,
                sanitized_text TEXT,
                hash_original TEXT,
                hash_sanitized TEXT,
                approval_timestamp DATETIME,
                user_id TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                record_uuid TEXT PRIMARY KEY,
                audit_id TEXT,
                timestamp TEXT,
                user_id TEXT,
                event_code TEXT,
                pii_hash TEXT,
                label TEXT,
                occurrence_index INT,
                confidence_score REAL,
                integrity_hash TEXT,
                commit_uuid TEXT,
                FOREIGN KEY (event_code) REFERENCES event_registry(event_code),
                FOREIGN KEY (commit_uuid) REFERENCES final_commit(commit_uuid)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_trail_audit_id ON audit_trail (audit_id)")

        # ── UI View ───────────────────────────────────────────────────────────
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS ui_highlight AS
                SELECT
                    p.pii_id, p.pii_text, p.filepath, p.pii_hash,
                    COALESCE(j.neutral, p.label) AS label,
                    p.occurrence_index, p.status, p.is_manual,
                    p.label AS category, r.event_code,
                    r.methodology, p.confidence_score
                FROM pending_pii p
                LEFT JOIN event_registry r ON p.event_code = r.event_code
                LEFT JOIN job_dict j ON p.pii_text = j.original
        """)

        # ── Users ─────────────────────────────────────────────────────────────
        init_users_table(cursor)

        # ── Seed job_dict ─────────────────────────────────────────────────────
        cursor.execute("SELECT COUNT(*) FROM job_dict")
        if cursor.fetchone()[0] == 0:
            if os.path.exists(CSV_PATH):
                seed_data = pd.read_csv(CSV_PATH)
                seed_data.to_sql('job_dict', conn, if_exists='append', index=False)
                print("[DB] job_dict seeded.")
            else:
                print(f"[DB] Warning: CSV not found at {CSV_PATH}")

        conn.commit()
    print("[DB] Schema initialized.")

def init_users_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'reviewer',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

def get_pending_data():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT filepath, markdown FROM pending_review WHERE status = 'PENDING'", conn)

# V1.1 with sort by confidence  
# def get_pending_data():
#     with sqlite3.connect(DB_PATH) as conn:
#         return pd.read_sql("""
#             SELECT 
#                 r.filepath,
#                 r.markdown,
#                 r.status,
#                 ROUND(AVG(p.confidence_score), 4) AS doc_confidence,
#                 COUNT(p.pii_id) AS pii_count
#             FROM pending_review r
#             LEFT JOIN pending_pii p ON r.filepath = p.filepath
#             WHERE r.status = 'PENDING'
#             GROUP BY r.filepath
#             ORDER BY doc_confidence ASC
#         """, conn)

def get_detected_data(filepath):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM ui_highlight WHERE filepath = ?", conn, params=(filepath,))

def toggle_pii_status(pii_id):
    #Toggles REDACT/EXCLUDE for a specific detection.
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE pending_pii 
            SET status = CASE
                WHEN status = 'REDACT' THEN 'EXCLUDE'
                WHEN status = 'EXCLUDE' THEN 'REDACT'
                ELSE status
            END
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

def certify_document(filepath, original_text, sanitized_text, user_id):
    c_uuid = str(uuid.uuid4())
    audit_id = hashlib.sha256(filepath.encode()).hexdigest()[:8].upper()
    hash_orig = hashlib.sha256(original_text.encode()).hexdigest()
    hash_sani = hashlib.sha256(sanitized_text.encode()).hexdigest()
    filename_hash = hashlib.sha256(os.path.basename(filepath).encode()).hexdigest()

    with sqlite3.connect(DB_PATH) as conn:
        # 1. Write to audit_trail before clearing pending_pii
        conn.execute("""
            INSERT INTO audit_trail (
                record_uuid, audit_id, timestamp, user_id,
                event_code, pii_hash, label,
                occurrence_index, confidence_score, commit_uuid
            )
            SELECT 
                lower(hex(randomblob(16))), ?, ?, ?,
                event_code, pii_hash, label,
                occurrence_index, confidence_score, ?
            FROM pending_pii
            WHERE filepath = ?
        """, (audit_id, datetime.now().isoformat(), user_id, c_uuid, filepath))

        # 2. Insert into final_commit — no PII, audit_id only
        conn.execute("""
            INSERT INTO final_commit (
                commit_uuid, audit_id, filename_hash, sanitized_text,
                hash_original, hash_sanitized,
                approval_timestamp, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c_uuid, audit_id, filename_hash, sanitized_text,
            hash_orig, hash_sani,
            datetime.now().isoformat(), user_id
        ))

        # 3. Clear workspace
        conn.execute("DELETE FROM pending_review WHERE filepath = ?", (filepath,))
        conn.execute("DELETE FROM pending_pii WHERE filepath = ?", (filepath,))
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
        conn.commit()

def restore_document(filepath, user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pending_review 
            SET status = 'PENDING' 
            WHERE filepath = ?
        """, (filepath,))
        conn.commit()

def get_discarded_documents():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT filepath
            FROM pending_review 
            WHERE status = 'VERWORFEN'
            ORDER BY filepath ASC
        """, conn)
    
def purge_discarded():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Get discarded filepaths first to clean pending_pii
        cursor.execute("SELECT filepath FROM pending_review WHERE status = 'VERWORFEN'")
        filepaths = [row[0] for row in cursor.fetchall()]
        for filepath in filepaths:
            cursor.execute("DELETE FROM pending_pii WHERE filepath = ?", (filepath,))
        cursor.execute("DELETE FROM pending_review WHERE status = 'VERWORFEN'")
        conn.commit()

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

def export_audit_xlsx(output_path):
    with sqlite3.connect(DB_PATH) as conn:
        df_commits = pd.read_sql("""
            SELECT 
                commit_uuid, audit_id, sanitized_text,
                hash_original, hash_sanitized,
                approval_timestamp, user_id
            FROM final_commit
            ORDER BY approval_timestamp DESC
        """, conn)
        df_audit = pd.read_sql("""
            SELECT
                a.record_uuid, a.audit_id, a.timestamp,
                a.user_id, a.event_code, a.label,
                a.occurrence_index, a.confidence_score,
                a.commit_uuid, e.methodology, e.legal_basis
            FROM audit_trail a
            LEFT JOIN event_registry e ON a.event_code = e.event_code
            ORDER BY a.timestamp DESC
        """, conn)

    export_path = Path(output_path) / f"Complyable_Audit_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    with pd.ExcelWriter(str(export_path), engine='openpyxl') as writer:
        df_commits.to_excel(writer, sheet_name='Abgeschlossene Dokumente', index=False)
        df_audit.to_excel(writer, sheet_name='Audit Trail', index=False)

    return export_path

def get_archived_documents():
    with sqlite3.connect(DB_PATH) as conn:
        tables = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        if 'final_commit' not in tables:
            return pd.DataFrame()
        return pd.read_sql("""
            SELECT 
                commit_uuid, audit_id, sanitized_text,
                hash_original, hash_sanitized,
                approval_timestamp, user_id
            FROM final_commit
            ORDER BY approval_timestamp DESC
        """, conn)

def find_duplicate(filename, file_hash):
    filename_hash = hashlib.sha256(filename.encode()).hexdigest()
    with sqlite3.connect(DB_PATH) as conn:
        tables = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]

        if 'pending_review' in tables:
            result = conn.execute("""
                SELECT filepath, status FROM pending_review
                WHERE filepath LIKE ?
            """, (f"%{filename}",)).fetchone()
            if result:
                filepath, status = result
                audit_id = hashlib.sha256(filepath.encode()).hexdigest()[:8].upper()
                return {
                    'found': True,
                    'location': 'staging',
                    'status': status,
                    'audit_id': audit_id
                }

        if 'final_commit' in tables:
            result = conn.execute("""
                SELECT audit_id FROM final_commit
                WHERE filename_hash = ?
            """, (filename_hash,)).fetchone()
            if result:
                return {
                    'found': True,
                    'location': 'archive',
                    'status': 'ARCHIVIERT',
                    'audit_id': result[0]
                }

        return {'found': False}

def get_audit_highlighter_df(commit_uuid):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT
                a.record_uuid as pii_id,
                a.pii_hash,
                a.label,
                a.occurrence_index,
                a.confidence_score,
                a.event_code,
                e.category,
                'REDACT' as status,
                0 as is_manual
            FROM audit_trail a
            LEFT JOIN event_registry e ON a.event_code = e.event_code
            WHERE a.commit_uuid = ?
        """, conn, params=(commit_uuid,))
    
def get_archived_by_commit(commit_uuid):
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute("""
            SELECT commit_uuid, audit_id, sanitized_text,
                   approval_timestamp, user_id
            FROM final_commit
            WHERE commit_uuid = ?
        """, (commit_uuid,)).fetchone()
        if result:
            return {
                'commit_uuid': result[0],
                'audit_id': result[1],
                'sanitized_text': result[2],
                'approval_timestamp': result[3],
                'user_id': result[4]
            }
        return None