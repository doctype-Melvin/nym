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

# -- Overlay component
CURRENT_DIR = Path(__file__).parent.absolute()
COMP_PATH = CURRENT_DIR / "overlay"

overlayer = components.declare_component("overlayer", path=str(COMP_PATH))

st.set_page_config(page_title="Complyable | Compliance Review", layout="wide")

# 2. SESSION STATE (The Idempotency Guard)
if "last_click_id" not in st.session_state:
    st.session_state.last_click_id = None

# 3. LOGIC FUNCTIONS
def apply_overlay(text, highlighter_df):
    from collections import defaultdict
    render_counts = defaultdict(int)
    
    # Sort by length to handle multi-word PII correctly
    highlighter_df['len'] = highlighter_df['pii_text'].str.len()
    sorted_df = highlighter_df.sort_values('len', ascending=False)

    processed_text = text
    for _, row in sorted_df.iterrows():
        word = row['pii_text']
        target_idx = row['occurrence_index']
        pii_id = row['pii_id']
        status = str(row['status']).lower()
        category_class = "gender" if str(row['category']).lower() == "gender" else "default"
        
        def count_and_replace(match):
            render_counts[word] += 1
            if render_counts[word] == target_idx:
                return f'<mark class="{category_class}" data-id="{pii_id}">{match.group(0)}</mark>'
            return match.group(0)

        pattern = rf'(?<!\w){re.escape(word)}(?!\w)'
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

    # Fetch data directly from DB view
    highlighter_df = get_detected_data(selected_file)
    row = df_pending[df_pending['filepath'] == selected_file].iloc[0]

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