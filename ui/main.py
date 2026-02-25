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


def apply_overlay(text, highlighter_df, file_manifest):
    # text: raw markdown content
    # highlighter_df: ui_highlight view with pipeline results
    # file_manifest: draft edits for this file -- st.session_state.draft_manifest[selected_file]

    pii_map = {}
    user_exclusions_text = []
    
    # n-gram (1-word, 2-word, 3-word combinations).
    # We iterate through the document and try to match 
    # based on common PII lengths (1 to 3 words).
    words = text.split()
    
    for i in range(len(words)):
        # Try up to 5-word combinations
        for n in range(1, 6): 
            if i + n > len(words):
                break
            
            phrase = " ".join(words[i:i+n]).strip('.,!?;:()[]"\'')
            phrase_hash = hashlib.sha256(phrase.encode()).hexdigest()
            
            # Check against DB results
            match = highlighter_df[highlighter_df['pii_hash'] == phrase_hash]
            
            if not match.empty: # this should be the label as per ui_highlight view
                category = match.iloc[0]['category']
                pii_map[phrase] = category
                
                # any draft exclusions
                if phrase_hash in file_manifest['exclusions']:
                    user_exclusions_text.append(phrase)
            
            # Check manual redactions in drafts
            if phrase_hash in file_manifest['manual_redactions']:
                manual_entry = file_manifest['manual_redactions'][phrase_hash]
                pii_map[phrase] = manual_entry['label']
    
    return pii_map, user_exclusions_text

def get_detected_data(filepath):
    with sqlite3.connect(DB_PATH) as conn:

        query = "SELECT pii_hash, category, event_code, label FROM ui_highlight WHERE filepath = ?"
        return pd.read_sql(query, conn, params=(filepath,))

def get_pending_data():
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT filepath, original, markdown, output, status FROM pending_review WHERE status = 'PENDING'"
        return pd.read_sql(query, conn)
    
def generate_live_redaction(text, highlighter_df, file_manifest):
    if not text:
        return ""
    
    # 1. Identify what needs to be redacted
    # AI detections MINUS exclusions
    active_machine = set(highlighter_df[~highlighter_df['pii_hash'].isin(file_manifest['exclusions'])]['pii_hash'])
    # PLUS manual marks
    manual_hashes = set(file_manifest['manual_redactions'].keys())
    
    all_to_redact = active_machine.union(manual_hashes)

    # 2. Process words
    words = text.split()
    final_output = []

    for word in words:
        # Keep punctuation attached to the word for the final look
        clean_word = word.strip('.,!?;:()[]"\'')
        h = hashlib.sha256(clean_word.encode()).hexdigest()

        if h in all_to_redact:
            # Check for a specific label
            if h in file_manifest['manual_redactions']:
                label = file_manifest['manual_redactions'][h]['label']
            else:
                match = highlighter_df[highlighter_df['pii_hash'] == h]
                label = match.iloc[0]['category'] if not match.empty else "PII"
            
            # Format as a clean tag: e.g. [VORNAME] or [MANUELL]
            # We preserve trailing punctuation like "Mustermann," -> "[VORNAME],"
            trailing_punctuation = word[len(clean_word.rstrip('.,!?;:()[]"\'')):]
            final_output.append(f"**[{label.upper()}]**{trailing_punctuation}")
        else:
            final_output.append(word)

    return " ".join(final_output)

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
    pii_map, exclusions = apply_overlay(
        row['markdown'], 
        highlighter_df,
        st.session_state.draft_manifest[selected_file]
    )
    
    js_response = overlayer(
        markdown=row['markdown'],
        pii_map=pii_map,
        user_exclusions=exclusions,
        key=f"ov_{selected_file}",
        height=700
    )


    if "last_processed_action" not in st.session_state:
        st.session_state.last_processed_action = None

# INTERACTION LOGIC
    # Toggle Action
    if js_response and js_response.get("action") == "toggle":
        current_action_id = js_response.get('click_id')
        if st.session_state.last_processed_action != current_action_id:
            word_to_toggle = js_response.get("word")
            h = hashlib.sha256(word_to_toggle.encode()).hexdigest()

            file_manifest = st.session_state.draft_manifest[selected_file]

            if h in file_manifest['manual_redactions']:
                del file_manifest['manual_redactions'][h]

            else:
                if h in file_manifest['exclusions']:
                    file_manifest['exclusions'].remove(h)
                else:
                    file_manifest['exclusions'].add(h)
            
            st.session_state.last_processed_action = current_action_id
            st.rerun()
    
    # Manual Tag Action
    # maybe make manual_mark a dict containing {mark: text, label: label}
    if js_response and js_response.get("action") == "manual_mark":
        current_action_id = js_response.get("click_id")

        if st.session_state.last_processed_action != current_action_id:
            new_pii = js_response.get("word")
            new_hash = hashlib.sha256(new_pii.encode()).hexdigest()

            file_manifest = st.session_state.draft_manifest[selected_file]

            file_manifest['manual_redactions'][new_hash] = {
                "text": new_pii,
                "label": "MANUELL"
            }

            st.session_state.last_processed_action = current_action_id
            st.rerun()

    with st.expander ("🛡️ Live Redaction Preview"):
        
        # Generate the text based on your toggles in Col 1
        live_redacted_text = generate_live_redaction(
            row['markdown'], 
            highlighter_df, 
            st.session_state.draft_manifest[selected_file]
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