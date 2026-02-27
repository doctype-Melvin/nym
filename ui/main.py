import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import hashlib
import re
import streamlit.components.v1 as components

# 1. SETUP & PATHS
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
DB_PATH = BASE_DIR / "data" / "vault" / "complyable_vault.db"

# --- Dropzone
UPLOAD_DIR = BASE_DIR / "data" / "input"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# --- KNIME
KNIME_EXE = r"/Applications/KNIME 5.4.2.app/Contents/MacOS/knime"
WORKFLOW_PATH = str(BASE_DIR / "knime" / "core-v1.knwf")

# -- Overlay component
CURRENT_DIR = Path(__file__).parent.absolute()
COMP_PATH = CURRENT_DIR / "overlay"

overlayer = components.declare_component("overlayer", path=str(COMP_PATH))

st.set_page_config(page_title="Complyable | Compliance Review", layout="wide")

def init_db_schema():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Create core tables if missing
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
            CREATE TABLE IF NOT EXISTS job_dict (
                original TEXT PRIMARY KEY,
                neutral TEXT
            )
        """)
        cursor.execute("""CREATE TABLE IF NOT EXISTS event_registry (
                event_code TEXT PRIMARY KEY,
                category TEXT, 
                source_tier TEXT,
                methodology TEXT,
                legal_basis TEXT
            )""")
        cursor.execute("DROP VIEW IF EXISTS ui_highlight")
        cursor.execute("""
            CREATE VIEW ui_highlight AS 
            SELECT
                p.pii_id, p.filepath, p.pii_text, p.pii_hash,
                COALESCE(j.neutral, p.label) AS label,
                p.occurrence_index, p.status, p.is_manual,
                p.label AS category,
                p.confidence_score
            FROM pending_pii p
            LEFT JOIN job_dict j ON p.pii_text = j.original
        """)
        conn.commit()

# Call this at the top of main.py
init_db_schema()

# 2. SESSION STATE (The Idempotency Guard)
if "last_click_id" not in st.session_state:
    st.session_state.last_click_id = None

if "editing_pii_id" not in st.session_state:
    st.session_state.editing_pii_id = None

# 3. LOGIC FUNCTIONS
def apply_overlay(text, highlighter_df):
    from collections import defaultdict
    render_counts = defaultdict(int)

    def get_ui_class(row):
        if str(row['status']).lower() == 'exclude':
            return "pii-excluded"
        lbl = str(row['category'])
        if lbl == "GEN-RE": return "gen-resolved"
        if lbl == "GEN-FL": return "gen-flagged"
        return "pii-default"
    
    # Sort by length to handle multi-word PII correctly
    #highlighter_df['len'] = highlighter_df['pii_text'].str.len()
    #sorted_df = highlighter_df.sort_values(by=['len'], ascending=False)
    highlighter_df['priority'] = highlighter_df['category'].apply(
    lambda x: 1 if x == "GEN-RE" else (2 if x == "GEN-FL" else 3)
    )
    sorted_df = highlighter_df.sort_values(by=['pii_text', 'occurrence_index', 'priority'])
    highlighter_df = sorted_df.drop_duplicates(subset=['pii_text', 'occurrence_index'], keep='first')

    processed_text = text
    # Crucial: Iterate by word group to keep render_counts scoped correctly
    for word, group in highlighter_df.groupby('pii_text'):
        # Reset counter for EACH unique word
        render_counts[word] = 0 
        
        pattern = rf'(?<!\w){re.escape(word)}(?!\w)'
        
        def count_and_replace(match):
            render_counts[word] += 1
            # Check if this specific occurrence (1, 2, 3...) is in our database
            match_row = group[group['occurrence_index'] == render_counts[word]]
            
            if not match_row.empty:
                r = match_row.iloc[0]
                ui_class = get_ui_class(r)
                lbl = r['label']
                # If label is a neutral word (not a code), show the arrow
                arrow = f" <small>→ {lbl}</small>" if lbl not in ["GEN-RE", "GEN-FL", "GENDER"] else ""
                return f'<mark class="{ui_class}" data-id="{r["pii_id"]}">{match.group(0)}{arrow}</mark>'
            
            return match.group(0)

        processed_text = re.sub(pattern, count_and_replace, processed_text)

    return processed_text

def get_detected_data(filepath):
    with sqlite3.connect(DB_PATH) as conn:
        # Pull everything from the view
        query = "SELECT * FROM ui_highlight WHERE filepath = ?"
        return pd.read_sql(query, conn, params=(filepath,))

def get_pending_data():
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT filepath, markdown FROM pending_review WHERE status = 'PENDING'"
        return pd.read_sql(query, conn)
    
def generate_live_redaction(text, highlighter_df):
    if not text or highlighter_df.empty:
        return text
    
    # Filter for active redactions only
    to_redact = highlighter_df[highlighter_df['status'] == 'REDACT'].copy()
    to_redact['len'] = to_redact['pii_text'].str.len()
    to_redact = to_redact.sort_values('len', ascending=False)

    processed_text = text
    for _, row in to_redact.iterrows():
        word = row['pii_text']
        label = row['category'] if row['category'] else 'PII'
        pattern = rf'\b{re.escape(word)}\b'
        replacement = f'**[{label.upper()}]**'
        processed_text = re.sub(pattern, replacement, processed_text)
    
    return processed_text

# 4. UI MAIN RENDER
st.title("Shield Complyable | Recruiter Review Portal")

with st.expander("📂 Upload New Documents", expanded=False):
    uploaded_files = st.file_uploader("Drop PDF or Markdown files here", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with open(UPLOAD_DIR / uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} files. Please run your KNIME workflow to process.")

df_pending = get_pending_data()

if df_pending.empty:
    st.success("No pending reviews. Everything is safe for AI use.")
else: 
    st.sidebar.header("Files to review")
    selected_file = st.sidebar.selectbox("Select a Document", df_pending['filepath'].tolist())
    
    st.sidebar.divider()
    st.sidebar.subheader('Manual Tagging')

    LABELS_ACTIVE = [
        "PERSON",
        "PLZ",
        "DATUM",
        "TELEFON",
        "ADRESSE",
        "E-MAIL",
        "ORT",
        "WEB_LINK"
    ]

    active_label = st.sidebar.selectbox(
        "Label für manuelle Markierung",
        options=LABELS_ACTIVE,
        help="Wähle das passende Label für die Textauswahl"
    )

    st.sidebar.divider()
    if st.session_state.editing_pii_id:
        with sqlite3.connect(DB_PATH) as conn:
            # Get details of the clicked item
            res = pd.read_sql("""
                SELECT pii_text, label, category 
                FROM ui_highlight WHERE pii_id = ?
            """, conn, params=(st.session_state.editing_pii_id,))
        
        if not res.empty and res.iloc[0]['category'].lower() == 'gender':
            row = res.iloc[0]
            word = row['pii_text']
            # If the label isn't 'GENDER', it means we already have a suggestion
            current_suggestion = row['label'] if row['label'] != "GENDER" else ""

            with st.sidebar.expander("✨ Gender Neutralizer", expanded=True):
                st.markdown(f"**Original:** `{word}`")
                
                new_val = st.text_input(
                    "Neutral phrasing:", 
                    value=current_suggestion,
                    placeholder="e.g., Fachkraft"
                )

                col1, col2 = st.columns(2)
                if col1.button("Save & Apply All"):
                    with sqlite3.connect(DB_PATH) as conn:
                        cur = conn.cursor()
                        # 1. Update ALL instances of this word in current file
                        cur.execute("""
                            UPDATE pending_pii SET label = ? 
                            WHERE filepath = ? AND pii_text = ? AND label = 'GENDER'
                        """, (new_val, selected_file, word))
                        
                        # 2. Add to master dictionary for future learning
                        cur.execute("""
                            INSERT OR REPLACE INTO job_dict (original, neutral) 
                            VALUES (?, ?)
                        """, (word, new_val))
                        conn.commit()
                    st.rerun()
                    
                if col2.button("Clear/Reset"):
                    st.session_state.editing_pii_id = None
                    st.rerun()

    # Fetch data directly from DB view
    highlighter_df = get_detected_data(selected_file)
    row = df_pending[df_pending['filepath'] == selected_file].iloc[0]
    print(highlighter_df.head())
    st.subheader("🔍 Highlight Review")

    # Interactive Overlay
    rendered_html = apply_overlay(row['markdown'], highlighter_df)
    js_response = overlayer(
        markdown=rendered_html,
        key=f"ov_{selected_file}",
        height=700
    )

    # 5. INTERACTION LOGIC
    if js_response:
        current_click_id = js_response.get("click_id")

        if current_click_id != st.session_state.last_click_id:
            st.session_state.last_click_id = current_click_id
            action = js_response.get("action")
            
            if action == "toggle":
                clicked_id = js_response.get('pii_id')
                st.session_state.editing_pii_id = clicked_id
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE pending_pii 
                        SET status = CASE WHEN status = 'REDACT' THEN 'EXCLUDE' ELSE 'REDACT' END
                        WHERE pii_id = ?
                    """, (clicked_id,))
                    conn.commit()
                st.rerun()

            elif action == "manual_mark":
                selected_text = js_response.get("word")
                label_to_apply = active_label
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM pending_pii WHERE filepath = ? AND pii_text = ?", (selected_file, selected_text))
                    new_idx = cursor.fetchone()[0] + 1
                    
                    cursor.execute("""
                        INSERT INTO pending_pii (filepath, pii_text, pii_hash, label, occurrence_index, confidence_score, event_code, status, is_manual)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        selected_file, selected_text, hashlib.sha256(selected_text.encode()).hexdigest(),
                        label_to_apply, new_idx, 1.0, "USER-UI", 'REDACT', 1
                    ))
                    conn.commit()   
                st.rerun()

    # 6. PREVIEW & APPROVAL
    with st.expander ("🛡️ Live Redaction Preview", expanded=True):
        live_redacted_text = generate_live_redaction(row['markdown'], highlighter_df)
        st.markdown(live_redacted_text)

    st.divider()

    if st.button("Final Approve & Sign", type="primary"):
        # Logic to finalize document and move staging to audit trail goes here
        st.balloons()
        st.success("Document finalized.")