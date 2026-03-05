"""
pipeline.py — Replaces core-v1.knwf
Drop-in replacement for the KNIME workflow.
Call run_pipeline(input_dir) from workflow.py instead of trigger_knime().
"""

import sqlite3
import pandas as pd
import re
import hashlib
import unicodedata
import os
import spacy
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

# --- Docling imports ---
from docling.document_converter import DocumentConverter

load_dotenv()

# --- CONFIG ---
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(BASE_DIR / "data" / "vault" / "complyable_vault.db")
CSV_PATH = str(BASE_DIR / "data" / "refs" / "dict_seed.csv")

# Load spaCy once at module level — expensive, only do it once
print("[Pipeline] Loading spaCy model...")
nlp = spacy.load("de_core_news_lg")
ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.add_patterns([
    {"label": "ADRESSE_1", "pattern": [{"TEXT": {"REGEX": r"(?i).+(straße|str\.|weg|platz|allee|gasse|damm)$"}}]},
    {"label": "ADRESSE_2", "pattern": [{"TEXT": {"REGEX": r"(?i).+(straße|str\.|weg|platz)$"}}, {"IS_DIGIT": True}]}
])
print("[Pipeline] spaCy model loaded.")

# ─────────────────────────────────────────────
# SHARED UTILITIES
# ─────────────────────────────────────────────

def make_pii_hash(text):
    clean_text = unicodedata.normalize('NFC', str(text)).strip()
    return hashlib.sha256(clean_text.encode('utf-8')).hexdigest()

def to_titlecase(text):
    text = re.sub(r'\b([A-ZÜÖÄ])(?:\s([A-ZÜÖÄ]))+\b',
                  lambda m: m.group(0).replace(" ", ""), text)
    def replace_match(match):
        word = match.group(0)
        return word.lower().title() if len(word) >= 3 else word
    return re.sub(r'\b[A-ZÜÖÄß]{3,}\b', replace_match, text)


# ─────────────────────────────────────────────
# STEP 0: SCHEMA GUARD (was: schema guard node)
# ─────────────────────────────────────────────

def initialize_vault():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_registry (
                event_code TEXT PRIMARY KEY,
                category TEXT,
                source_tier TEXT,
                methodology TEXT,
                legal_basis TEXT
            )
        """)
        events = [
            ('T0-ANL', 'System', 'Tier 0', 'Tika Parser Metadata Analysis', 'System Integrity'),
            ('T1-RGX', 'Privacy', 'Tier 1', 'Deterministic REGEX Matching', 'GDPR / DSGVO'),
            ('T2-NER', 'Privacy', 'Tier 2', 'Probabilistic Named Entity Recognition', 'GDPR / DSVGO'),
            ('T3-GIP', 'Inclusion', 'Tier 3', 'Linguistic Gender Neutralization', 'AGG / EU AI Act'),
            ('T3-FLG', 'Inclusion', 'Tier 3', 'Morphological Gender Flagging', 'EU AI Act / D&I'),
            ('USR-RED', 'Privacy', 'User', 'Manual Redaction/Labeling', 'GDPR / DSGVO / Data Minimization'),
            ('USR-GIP', 'Inclusion', 'User', 'Manual gender-neutralization', 'AGG / EU AI Act')
        ]
        cursor.executemany("INSERT OR IGNORE INTO event_registry VALUES (?, ?, ?, ?, ?)", events)

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

        cursor.execute("DROP TABLE IF EXISTS job_dict")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_dict (
                original TEXT PRIMARY KEY,
                neutral TEXT,
                category TEXT
            )
        """)
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
        cursor.execute("DROP VIEW IF EXISTS ui_highlight")
        cursor.execute("""
            CREATE VIEW ui_highlight AS
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                record_uuid TEXT PRIMARY KEY,
                filepath TEXT,
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_filepath ON audit_trail (filepath)")

        # Seed job_dict if empty
        cursor.execute("SELECT COUNT(*) FROM job_dict")
        if cursor.fetchone()[0] == 0:
            if os.path.exists(CSV_PATH):
                seed_data = pd.read_csv(CSV_PATH)
                seed_data.to_sql('job_dict', conn, if_exists='append', index=False)
                print("[Pipeline] job_dict seeded.")
            else:
                print(f"[Pipeline] Warning: CSV not found at {CSV_PATH}")

        conn.commit()
    print("[Pipeline] Vault initialized.")


# ─────────────────────────────────────────────
# STEP 1: DOCLING PARSER (was: Tika + chunk loop)
# ─────────────────────────────────────────────

def parse_documents(input_dir):
    """
    Replaces the Tika Parser node + chunk loop.
    Returns a list of dicts: {filepath, original, markdown}
    """
    converter = DocumentConverter()
    input_path = Path(input_dir)
    supported = {".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".html", ".txt"}
    files = [f for f in input_path.iterdir() if f.suffix.lower() in supported]

    if not files:
        print(f"[Pipeline] No supported files found in {input_dir}")
        return []

    results = []
    for filepath in files:
        print(f"[Pipeline] Parsing: {filepath.name}")
        try:
            result = converter.convert(str(filepath))
            markdown_text = result.document.export_to_markdown()
            results.append({
                "filepath": str(filepath),
                "original": markdown_text,
                "markdown": markdown_text,
            })
        except Exception as e:
            print(f"[Pipeline] ERROR parsing {filepath.name}: {e}")

    print(f"[Pipeline] Parsed {len(results)} documents.")
    return results


# ─────────────────────────────────────────────
# STEP 2: TIER 1 — REGEX (was: Tier 1 node)
# ─────────────────────────────────────────────

TIER1_REGEX = [
    {"label": "E-MAIL",       "pattern": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"},
    {"label": "TELEFON",      "pattern": r"(?:(?:\+?49[ \-\.\(\)]?)?(?:(?:\(?0\d{1,5}\)?)|(?:\d{1,5}))[ \-\.\(\)]?(?:\d[ \-\.\(\)]?){5,10}\d)"},
    {"label": "WEB_LINK",     "pattern": r"\b(?<!mailto:)(?<!@)(?:https?:\/\/)?(?:www\.)?(?!\d)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:\/[^\s<>\"'@]*|(?!\S))?\b(?![\w@./])"},
    {"label": "SOCIAL_MEDIA", "pattern": r"@[A-Za-z0-9](?:[A-Za-z0-9._-]{1,28}[A-Za-z0-9])?"},
    {"label": "PLZ",          "pattern": r"\b\d{5}\b"},
    {"label": "DATUM",        "pattern": r"\b\d{1,2}\.\d{1,2}\.(\d{4}|\d{2})\b"},
    {"label": "DATUM",        "pattern": r"(?i)\b\d{1,2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s\d{4}\b"},
    {"label": "DATUM",        "pattern": r"(?i)\b\d{2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s\d{4}\b"},
    {"label": "DATUM",        "pattern": r"(?i)\b\d{1,2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s'\d{2}\b"},
]

def run_tier1(docs):
    """Runs regex matching on all documents. Returns enriched docs + cumulative log."""
    cumulative_log = []

    for doc in docs:
        text = to_titlecase(unicodedata.normalize('NFC', doc['markdown']))
        filepath = doc['filepath']
        occ_counter = defaultdict(int)

        for rule in TIER1_REGEX:
            for match in re.finditer(rule['pattern'], text, flags=re.IGNORECASE):
                match_text = match.group()
                occ_counter[match_text] += 1
                cumulative_log.append({
                    'filepath': filepath,
                    'pii_text': match_text,
                    'pii_hash': make_pii_hash(match_text),
                    'label': rule['label'],
                    'occurrence_index': occ_counter[match_text],
                    'confidence_score': 1.0,
                    'event_code': 'T1-RGX',
                    'status': 'REDACT',
                    'is_manual': 0
                })
                text = text.replace(match_text, f"[{rule['label']}]")

        doc['output'] = text
        doc['markdown'] = doc['markdown']  # preserve original markdown

    print(f"[Pipeline] Tier 1 complete. {len(cumulative_log)} findings.")
    return docs, cumulative_log


# ─────────────────────────────────────────────
# STEP 3: TIER 2 — spaCy NER (was: Tier 2 node)
# ─────────────────────────────────────────────

ENT_LABELS = {
    "PER": "PERSON",
    "LOC": "ORT",
    "PHONE": "TELEFON",
    "EMAIL": "E-MAIL",
    "ADRESSE_1": "ADRESSE",
    "ADRESSE_2": "ADRESSE"
}

def get_beam_confidence(doc, beam_width=16, beam_density=0.0001):
    ner = nlp.get_pipe("ner")
    beams = ner.beam_parse([doc], beam_width=beam_width, beam_density=beam_density)
    entity_scores = defaultdict(float)
    for beam in beams:
        for score, ents in ner.moves.get_beam_parses(beam):
            for start, end, label in ents:
                entity_scores[(start, end, label)] += score
    return entity_scores

def run_tier2(docs, prior_log):
    cumulative_log = list(prior_log)

    for doc in docs:
        text = doc['markdown']
        filepath = doc['filepath']
        spacy_doc = nlp(text)
        beam_scores = get_beam_confidence(spacy_doc)
        occ_counter = defaultdict(int)

        for ent in spacy_doc.ents:
            if ent.label_ in ENT_LABELS or ent.label_.startswith("ADRESSE_"):
                found_text = ent.text
                label = ENT_LABELS.get(ent.label_, ent.label_)
                occ_counter[found_text] += 1
                score_key = (ent.start, ent.end, ent.label_)
                conf = 1.0 if (ent.ent_id_ or ent.label_ in ['ADRESSE_1', 'ADRESSE_2']) \
                       else round(float(beam_scores.get(score_key, 0.0)), 4)

                cumulative_log.append({
                    'filepath': filepath,
                    'pii_text': found_text,
                    'pii_hash': make_pii_hash(found_text),
                    'label': label,
                    'occurrence_index': occ_counter[found_text],
                    'confidence_score': conf,
                    'event_code': 'T2-NER',
                    'status': 'REDACT',
                    'is_manual': 0
                })
                text = re.sub(rf'\b{re.escape(found_text)}\b', f"[{label}]", text)

        doc['markdown'] = text

    print(f"[Pipeline] Tier 2 complete. {len(cumulative_log)} total findings so far.")
    return docs, cumulative_log


# ─────────────────────────────────────────────
# STEP 4: TIER 3 — Gender (was: Tier 3 node)
# ─────────────────────────────────────────────

def is_person_related(token):
    text = token.text.lower()
    blacklist = {"september", "oktober", "november", "dezember"}
    if text in blacklist or token.ent_type_ in ["DATE", "TIME", "CARDINAL"]:
        return False
    person_suffixes = ("er", "in", "ent", "ant", "ist", "kraft", "experte", "leiter")
    return text.endswith(person_suffixes) or token.ent_type_ == "PER"

def run_tier3(docs, prior_log):
    cumulative_log = list(prior_log)

    # Load job_dict from DB
    with sqlite3.connect(DB_PATH) as conn:
        job_table = pd.read_sql_query("SELECT original, neutral FROM job_dict", conn)
    job_table = job_table.iloc[job_table['original'].str.len().argsort()[::-1]].reset_index(drop=True)

    kauf_patterns = [
        (r"\b(\w+)(kaufmann|kauffrau)\b", r"\1fachkraft", "GEN-RE"),
        (r"\b(Kaufmann|Kauffrau)\s+für\b", "Fachkraft für", "GEN-RE"),
        (r"\b(Kaufmann|Kauffrau)\s\b", "Fachkraft ", "GEN-RE")
    ]

    for doc in docs:
        current = doc['markdown']
        filepath = doc['filepath']
        occ_counter = defaultdict(int)
        handle_indices = set()

        # 1. Kauf patterns
        for pattern, replacement, label in kauf_patterns:
            for match in re.finditer(pattern, current, flags=re.IGNORECASE):
                match_text = match.group()
                occ_counter[match_text] += 1
                cumulative_log.append({
                    'filepath': filepath,
                    'pii_text': match_text,
                    'pii_hash': make_pii_hash(match_text),
                    'label': label,
                    'occurrence_index': occ_counter[match_text],
                    'confidence_score': 1.0,
                    'event_code': 'T3-GIP',
                    'status': 'REDACT',
                    'is_manual': 0
                })
            current = re.sub(pattern, replacement, current, flags=re.IGNORECASE)

        # 2. Dictionary lookup
        for _, d_row in job_table.iterrows():
            original = str(d_row['original'])
            target = rf'\b{re.escape(original)}\b'
            for match in re.finditer(target, current, flags=re.IGNORECASE):
                actual_text = match.group()
                occ_counter[actual_text] += 1
                cumulative_log.append({
                    'filepath': filepath,
                    'pii_text': actual_text,
                    'pii_hash': make_pii_hash(actual_text),
                    'label': "GEN-RE",
                    'occurrence_index': occ_counter[actual_text],
                    'confidence_score': 0.9,
                    'event_code': 'T3-GIP',
                    'status': 'REDACT',
                    'is_manual': 0
                })
                for i in range(match.start(), match.end()):
                    handle_indices.add(i)
            current = re.sub(target, d_row["neutral"], current, flags=re.IGNORECASE)

        # 3. Linguistic flagging
        spacy_doc = nlp(doc['markdown'])
        for token in spacy_doc:
            if token.idx in handle_indices:
                continue
            if token.pos_ in ["NOUN", "PROPN"]:
                morph = token.morph.to_dict()
                gender = morph.get("Gender")
                if is_person_related(token) and gender in ['Fem', 'Masc']:
                    if any(token.text.lower().endswith(s) for s in ['in', 'innen', 'er', 'erin']):
                        occ_counter[token.text] += 1
                        cumulative_log.append({
                            'filepath': filepath,
                            'pii_text': token.text,
                            'pii_hash': make_pii_hash(token.text),
                            'label': "GEN-FL",
                            'occurrence_index': occ_counter[token.text],
                            'confidence_score': 0.75,
                            'event_code': 'T3-FLG',
                            'status': 'REDACT',
                            'is_manual': 0
                        })

        doc['markdown'] = current

    print(f"[Pipeline] Tier 3 complete. {len(cumulative_log)} total findings.")
    return docs, cumulative_log


# ─────────────────────────────────────────────
# STEP 5: WRITE TO DB (was: DB Writer node)
# ─────────────────────────────────────────────

def write_to_db(docs, cumulative_log):
    with sqlite3.connect(DB_PATH) as conn:
        # Write documents to pending_review
        for doc in docs:
            conn.execute("""
                INSERT OR REPLACE INTO pending_review 
                    (filepath, original, markdown, output, status, integrity_hash)
                VALUES (?, ?, ?, ?, 'PENDING', ?)
            """, (
                doc['filepath'],
                doc['original'],
                doc['markdown'],
                doc.get('output', doc['markdown']),
                make_pii_hash(doc['original'])
            ))

        # Write PII findings to pending_pii
        if cumulative_log:
            log_df = pd.DataFrame(cumulative_log)
            log_df.to_sql('pending_pii', conn, if_exists='append', index=False)

        conn.commit()
    print(f"[Pipeline] Written {len(docs)} docs and {len(cumulative_log)} PII findings to DB.")


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

def run_pipeline(input_dir):
    """
    Main entry point. Call this from workflow.py instead of trigger_knime().
    Returns (success: bool, message: str)
    """
    try:
        print(f"[Pipeline] Starting. Input dir: {input_dir}")

        # Step 0: Ensure DB schema exists
        initialize_vault()

        # Step 1: Parse documents with Docling
        docs = parse_documents(input_dir)
        if not docs:
            return False, "No documents found in input directory."

        # Step 2: Tier 1 — Regex
        docs, log = run_tier1(docs)

        # Step 3: Tier 2 — spaCy NER
        docs, log = run_tier2(docs, log)

        # Step 4: Tier 3 — Gender neutralization
        docs, log = run_tier3(docs, log)

        # Step 5: Write everything to SQLite
        write_to_db(docs, log)

        print(f"[Pipeline] Complete. {len(docs)} documents processed.")
        return True, f"{len(docs)} documents processed successfully."

    except Exception as e:
        import traceback
        return False, f"Pipeline error: {str(e)}\n{traceback.format_exc()}"