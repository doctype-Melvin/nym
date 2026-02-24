import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import sys
import html
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

# 3. LOGIC FUNCTIONS
def toggle_pii(word_hash):
    if word_hash in st.session_state.user_exclusions:
        st.session_state.user_exclusions.remove(word_hash)
    else:
        st.session_state.user_exclusions.add(word_hash)

def apply_overlay(markdown_text, highlighter_df):
    if not markdown_text or highlighter_df.empty:
        return {}

    pii_lookup = {}
    # Use regex to find all words to ensure we match what the JS will see
    unique_words = set(re.findall(r'\b\w+\b', markdown_text))
    
    for word in unique_words:
        # Match the Python hashing logic used in your pipeline
        h = hashlib.sha256(word.encode()).hexdigest()
        match = highlighter_df[highlighter_df['pii_hash'] == h]
        
        if not match.empty:
            # We send the category so JS knows which color to use
            pii_lookup[word] = match['category'].values[0]
            
    return pii_lookup

def get_detected_data(filepath):
    with sqlite3.connect(DB_PATH) as conn:

        query = "SELECT pii_hash, category, event_code FROM ui_highlight WHERE filepath = ?"
        return pd.read_sql(query, conn, params=(filepath,))

def get_pending_data():
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT filepath, original, markdown, output, status FROM pending_review WHERE status = 'PENDING'"
        return pd.read_sql(query, conn)
    
def generate_live_redaction(text, highlighter_df, user_exclusions):
    """
    Produces the final redacted string based on current user decisions
    """
    if not text:
        return ""
    
    # Create a lookup for what SHOULD be redacted
    # Only include hashes that are NOT in the revoked set
    active_redactions = highlighter_df[~highlighter_df['pii_hash'].isin(user_exclusions)]
    redact_lookup = dict(zip(active_redactions['pii_hash'], active_redactions['event_code']))

    words = text.split()
    final_output = []

    for word in words:
        clean_word = word.strip('.,!?;:()')
        h = hashlib.sha256(clean_word.encode()).hexdigest()

        if h in redact_lookup:
            # Replace with the tag from event_code (e.g., [PER])
            tag = redact_lookup[h].split('-')[-1]
            final_output.append(f"[{tag}]")
        else:
            final_output.append(word)

    return " ".join(final_output)

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
    
    row = df_pending[df_pending['filepath'] == selected_file].iloc[0]
    highlighter_df = get_detected_data(selected_file)

    st.subheader("🔍 Highlight Review")
    
    pii_map = apply_overlay(
        row['markdown'], 
        highlighter_df
    )

    js_response = overlayer(
        markdown=row['markdown'],
        pii_map=pii_map,
        user_exclusions=list(st.session_state.user_exclusions),
        key=f"ov_{selected_file}",
        height=700
    )

    if js_response and js_response.get("action") == "toggle":
        word_to_toggle = js_response.get("word")
        h = hashlib.sha256(word_to_toggle.encode()).hexdigest()

        if h in st.session_state.user_exclusions:
            st.session_state.user_exclusions.remove(h)
        else:
            st.session_state.user_exclusions.add(h)
        st.rerun()
    
    with st.expander ("🛡️ Live Redaction Preview"):
        
        # Generate the text based on your toggles in Col 1
        live_redacted_text = generate_live_redaction(
            row['markdown'], 
            highlighter_df, 
            st.session_state.user_exclusions
        )
        
        # Show the result in the editor
        st.text_area("Finalized Output", value=live_redacted_text, height=500, key="live_editor")

    st.divider()

    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("Approve & Sign", type="primary"):
            # Update the database
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                
                # create override table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS manual_overrides (
                        filepath TEXT,
                        pii_hash TEXT,
                        decision TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 2. Update the pending_review table
                cursor.execute("""
                    UPDATE pending_review 
                    SET output = ?, status = 'CLEAN' 
                    WHERE filepath = ?
                """, (live_redacted_text, selected_file))
                
                # 3. Log every 'Revoke' decision made during this session
                for h in st.session_state.user_exclusions:
                    cursor.execute("""
                        INSERT INTO manual_overrides (filepath, pii_hash, decision)
                        VALUES (?, ?, 'REVOKED')
                    """, (selected_file, h))
                
                conn.commit()
            
            st.session_state.user_exclusions = set()
            
            st.success(f"Document {selected_file} signed and moved to Audit Trail.")
            st.balloons()
            st.rerun()