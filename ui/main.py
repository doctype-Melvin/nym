import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import html
import hashlib
import uuid
import re
import streamlit.components.v1 as components

# 1. SETUP & PATHS
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
DB_PATH = BASE_DIR / "data" / "vault" / "complyable_vault.db"

# -- Overlay component
CURRENT_DIR = Path(__file__).parent.absolute()
COMP_PATH = CURRENT_DIR / "overlay"

overlayer = components.declare_component(
        "overlayer",
        path=str(COMP_PATH)
    )
if not COMP_PATH.exists():
    st.error(f"Component folder not found at: {COMP_PATH}")

st.set_page_config(page_title="Complyable | Compliance Review", layout="wide")

# 2. SESSION STATE
if "last_click_id" not in st.session_state:
    st.session_state.last_click_id = None

if 'user_exclusions' not in st.session_state:
    st.session_state.user_exclusions = set()

if "draft_manifest" not in st.session_state:
    st.session_state.draft_manifest = {}

# 3. LOGIC FUNCTIONS
def toggle_pii(word_hash):
    if word_hash in st.session_state.user_exclusions:
        st.session_state.user_exclusions.remove(word_hash)
    else:
        st.session_state.user_exclusions.add(word_hash)


def apply_overlay(text, highlighter_df):
    import re
    from collections import defaultdict

    # text: raw markdown content
    # highlighter_df: ui_highlight view with pipeline results
    
    # 1. Track how many times we've seen a word during THIS specific render
    render_counts = defaultdict(int)
    
    # 2. Sort by string length (longest first)

    highlighter_df['len'] = highlighter_df['pii_text'].str.len()
    sorted_df = highlighter_df.sort_values('len', ascending=False)

    processed_text = text

    # 3. Use the DB records to surgically place tags
    for _, row in sorted_df.iterrows():
        word = row['pii_text']
        target_idx = row['occurrence_index']
        pii_id = row['pii_id']
        status = row['status'] 
        
        # This function runs for every regex match found
        def count_and_replace(match):
            render_counts[word] += 1
            # If this instance matches the occurrence_index
            if render_counts[word] == target_idx:
                # Wrap in a tag the UI can recognize
                return f'<mark class="{str(status).lower()}" data-id="{pii_id}">{match.group(0)}</mark>'
            return match.group(0)

        # Word boundary \b ensures we don't match 'alt' inside 'Halter'
        pattern = rf'\b{re.escape(word)}\b'
        processed_text = re.sub(pattern, count_and_replace, processed_text)

    return processed_text

def get_detected_data(filepath):
    with sqlite3.connect(DB_PATH) as conn:

        query = "SELECT pii_id, pii_hash, pii_text, occurrence_index, status, category, event_code, label FROM ui_highlight WHERE filepath = ?"
        return pd.read_sql(query, conn, params=(filepath,))

def get_pending_data():
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT filepath, original, markdown, output, status FROM pending_review WHERE status = 'PENDING'"
        return pd.read_sql(query, conn)
    
def generate_live_redaction(text, highlighter_df):
    if not text or highlighter_df.empty:
        return text
    
    import re
    
    # copy the pii_text
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

def save_manual_redaction_mock(filepath, word_to_hash, category="MANUAL"):
    """
    Prints the payload for verification without touching the DB.
    """
    pii_hash = hashlib.sha256(word_to_hash.encode()).hexdigest()
    
    # Mock database payload
    payload = {
        "filepath": filepath,
        "pii_hash": pii_hash,
        "category": category,
        "event_code": "MANUAL_01",
        "timestamp": "2026-02-24 15:00:00" # Placeholder
    }
    
    print("--- DB WRITE SIMULATION ---")
    print(f"Captured Word: '{word_to_hash}'")
    print(f"Payload to SQL: {payload}")
    print("---------------------------")

def save_manual_redaction_live(filepath, word_to_hash, category="MANUAL"):
    """
    Persists the manual redaction hash to the SQLite audit trail.
    """
    pii_hash = hashlib.sha256(word_to_hash.encode()).hexdigest()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # We use INSERT OR IGNORE to prevent duplicate hashes for the same file
            query = """
                INSERT OR IGNORE INTO ui_highlight 
                (filepath, pii_hash, category, event_code, created_at)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (filepath, pii_hash, category, "MANUAL_01", ts))
            conn.commit()
            return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False

# 4. STYLING
st.markdown("""
    <style>
    div.stButton > button {
        border: none; padding: 0px 4px; background-color: transparent;
        display: inline; margin: 0; font-family: inherit;
    }
    /* Simple CSS classes for button highlights */
    .pii-active { background-color: #ffcdd2; border-bottom: 2px solid red; }
    .gin-active { background-color: #fff9c4; border-bottom: 2px solid #ffd600; }
    </style>
""", unsafe_allow_html=True)

# 5. UI MAIN RENDER
st.title("Shield Complyable | Recruiter Review Portal")

df_pending = get_pending_data()

if df_pending.empty:
    st.success("No pending reviews. Everything is safe for AI use.")
else: 
    st.sidebar.header("Files to review")
    selected_file = st.sidebar.selectbox("Select a Document", df_pending['filepath'].tolist())
    
    if selected_file not in st.session_state.draft_manifest:
        st.session_state.draft_manifest[selected_file] = {
            "exclusions": set(),
            "manual_redactions": {},
            "neutralizations": {}
        }

    row = df_pending[df_pending['filepath'] == selected_file].iloc[0]
    highlighter_df = get_detected_data(selected_file)

    st.subheader("🔍 Highlight Review")

    # Call the highlighting overlay
    rendered_html = apply_overlay(
        row['markdown'], 
        highlighter_df
    )
    
    js_response = overlayer(
        markdown=rendered_html,
        key=f"ov_{selected_file}",
        height=700
    )


    if "last_processed_action" not in st.session_state:
        st.session_state.last_processed_action = None

# INTERACTION LOGIC
    # Toggle Action
    if js_response:
        current_click_id = js_response.get("click_id")

        if current_click_id != st.session_state.last_click_id:
            st.session_state.last_click_id = current_click_id

            action = js_response.get("action")
            
            if action == "toggle":
                clicked_id = js_response.get('pii_id')

                #SQL logic - status flip for detected pii
                with sqlite3.connect(DB_PATH) as connect:
                    cursor = connect.cursor()
                    cursor.execute("""
                        UPDATE pending_pii 
                        SET status = CASE 
                            WHEN status = 'REDACT' THEN 'EXCLUDE' 
                            ELSE 'REDACT' 
                        END
                        WHERE pii_id = ?
                    """, (clicked_id,))
                    connect.commit()
                st.rerun()
    # Manual Tag Action
            elif action == "manual_mark":
                selected_text = js_response.get("word")
                
                with sqlite3.connect(DB_PATH) as connect:
                    cursor = connect.cursor()
                    
                    # 1. Determine the occurrence_index for this manual selection
                    # We count how many times this text appears in the raw markdown
                    # This ensures the highlighter stays on the right instance.
                    raw_markdown = row['markdown']
                    # We use a non-overlapping count up to the point of selection 
                    # (Simplification: just get total count and set as next index)
                    cursor.execute("""
                        SELECT COUNT(*) FROM pending_pii 
                        WHERE filepath = ? AND pii_text = ?
                    """, (selected_file, selected_text))
                    existing_count = cursor.fetchone()[0]
                    
                    new_idx = existing_count + 1

                    # 2. Insert into pending_pii
                    cursor.execute("""
                        INSERT INTO pending_pii (
                            filepath, pii_text, pii_hash, label, 
                            occurrence_index, confidence_score, 
                            event_code, status, is_manual
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        selected_file, 
                        selected_text, 
                        hashlib.sha256(selected_text.encode()).hexdigest(),
                        "MANUAL",       # Label it as manual
                        new_idx, 
                        1.0,            # Manual is always 100% confident
                        "USER-UI",      # Custom event code
                        'REDACT',       # Default to redacted
                        1               # is_manual = True
                    ))
                    connect.commit()   
                st.rerun()

    with st.expander ("🛡️ Live Redaction Preview"):
        
        # Generate the text based on your toggles in Col 1
        live_redacted_text = generate_live_redaction(
            row['markdown'], 
            highlighter_df
        )
        
        # Show the result in the editor
        st.markdown(live_redacted_text)

    st.divider()

    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("Approve & Sign", type="primary"):
            file_manifest = st.session_state.draft_manifest[selected_file]
            ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            # Update the database
            try: 

                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()

                    for pii_hash, data in file_manifest["manual_redactions"].items():
                        record_uuid = str(uuid.uuid4())
                        integrity_blob = f"{record_uuid}{selected_file}{pii_hash}"
                        integrity_hash = hashlib.sha256(integrity_blob.encode()).hexdigest()
                        
                        cursor.execute("""
                            INSERT INTO audit_trail
                                       (record_uuid, filepath, timestamp, event_code, pii_hash, label, confidence_score, integrity_hash)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            record_uuid,
                            selected_file,
                            ts,
                            "MANUAL_01",
                            pii_hash,
                            data['label'],
                            1.0,
                            integrity_hash
                        ))
                
                # create override table
                # cursor.execute("""
                #     CREATE TABLE IF NOT EXISTS manual_overrides (
                #         filepath TEXT,
                #         pii_hash TEXT,
                #         decision TEXT,
                #         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                #     )
                # """)

                # 2. Update the pending_review table
                    cursor.execute("""
                        UPDATE pending_review 
                        SET output = ?, status = 'CLEAN' 
                        WHERE filepath = ?
                    """, (live_redacted_text, selected_file))
                    
                    conn.commit()
                # 3. Log every 'Revoke' decision made during this session
                # for h in st.session_state.user_exclusions:
                #     cursor.execute("""
                #         INSERT INTO manual_overrides (filepath, pii_hash, decision)
                #         VALUES (?, ?, 'REVOKED')
                #     """, (selected_file, h))
                
                del st.session_state.draft_manifest[selected_file]
                st.balloons()
            
                st.success(f"Document {selected_file} signed and moved to Audit Trail.")
                remaining = len(get_pending_data())
                if remaining > 0:
                    st.info(f"Gute Arbeit! Nur noch **{remaining}** verbleibende Dokumente.")
                else:
                    st.snow()
                    st.success("**Keine offenen Dokumente mehr!**")
                
                import time
                time.sleep(2)
                st.rerun()
            
            except Exception as e:
                st.error(f"Commit failed: {e}")