import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import sys
import html
import hashlib
import re

# 1. SETUP & PATHS
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
DB_PATH = BASE_DIR / "data" / "vault" / "complyable_vault.db"

st.set_page_config(page_title="Complyable | Compliance Review", layout="wide")

# 2. SESSION STATE
if 'revoked_hashes' not in st.session_state:
    st.session_state.revoked_hashes = set()

# 3. LOGIC FUNCTIONS
def toggle_pii(word_hash):
    if word_hash in st.session_state.revoked_hashes:
        st.session_state.revoked_hashes.remove(word_hash)
    else:
        st.session_state.revoked_hashes.add(word_hash)

def apply_overlay(markdown_text, highlighter_df, revoked_hashes):
    """
    Wraps detected PII in the raw markdown with HTML spans 
    without breaking the markdown structure.
    """
    if not markdown_text:
        return ""
    
    # Start with a safe version of the text
    processed_text = html.escape(markdown_text)
    
    # Check every unique word in the document
    unique_words = set(markdown_text.split())
    
    for word in unique_words:
        clean_word = word.strip('.,!?;:()')
        h = hashlib.sha256(clean_word.encode()).hexdigest()
        
        # Match against our database of detected PII
        match = highlighter_df[highlighter_df['pii_hash'] == h]
        
        if not match.empty:
            category = match['category'].values[0]
            is_revoked = h in revoked_hashes
            
            # Styling for the "Glass Box"
            if is_revoked:
                style = "background-color: #e0e0e0; text-decoration: line-through; color: #888; border-radius: 3px;"
            else:
                color = "#ffcdd2" if category == 'Privacy' else "#fff9c4"
                style = f"background-color: {color}; border-radius: 3px; padding: 0 2px; font-weight: 500;"
            
            # Create the HTML Span
            # Note: We'll add the 'click' logic in the next step
            span = f'<span style="{style}" title="{category}">{html.escape(word)}</span>'
            
            # Use Regex to replace only whole words (\b)
            # This ensures 'Schmidt' is caught but not 'Schmidt' inside 'Schmidt-Group'
            pattern = rf'\b{re.escape(html.escape(word))}\b'
            processed_text = re.sub(pattern, span, processed_text)

    # Convert escaped Markdown structural elements back so Streamlit can render them
    # This allows ##, *, and line breaks to work again
    processed_text = processed_text.replace("&gt;", ">").replace("&lt;", "<").replace("\n", "<br>")
    return processed_text

def get_detected_data(filepath):
    with sqlite3.connect(DB_PATH) as conn:

        query = "SELECT pii_hash, category, event_code FROM ui_highlight WHERE filepath = ?"
        return pd.read_sql(query, conn, params=(filepath,))

def get_pending_data():
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT filepath, original, markdown, output, status FROM pending_review WHERE status = 'PENDING'"
        return pd.read_sql(query, conn)
    
def generate_live_redaction(text, highlighter_df, revoked_hashes):
    """
    Produces the final redacted string based on current user decisions
    """
    if not text:
        return ""
    
    # Create a lookup for what SHOULD be redacted
    # Only include hashes that are NOT in the revoked set
    active_redactions = highlighter_df[~highlighter_df['pii_hash'].isin(revoked_hashes)]
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

    col1, col2 = st.columns(2)

    with col1: 
        st.subheader("🔍 Glass Box Review")
        
        # Generate the beautiful, structure-preserved markup
        markup = apply_overlay(
            row['markdown'], 
            highlighter_df, 
            st.session_state.revoked_hashes
        )
        
        # Render the whole thing as one block
        # white-space: pre-wrap; is the key to keeping your manual line breaks!
        st.markdown(
            f'<div style="font-family: sans-serif; white-space: pre-wrap; line-height: 1.6;">{markup}</div>', 
            unsafe_allow_html=True
        )

    with col2:
        st.subheader("🛡️ Live Redaction Preview")
        
        # Generate the text based on your toggles in Col 1
        live_redacted_text = generate_live_redaction(
            row['markdown'], 
            highlighter_df, 
            st.session_state.revoked_hashes
        )
        
        # Show the result in the editor
        st.text_area("Finalized Output", value=live_redacted_text, height=600, key="live_editor")

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
                for h in st.session_state.revoked_hashes:
                    cursor.execute("""
                        INSERT INTO manual_overrides (filepath, pii_hash, decision)
                        VALUES (?, ?, 'REVOKED')
                    """, (selected_file, h))
                
                conn.commit()
            
            st.session_state.revoked_hashes = set()
            
            st.success(f"Document {selected_file} signed and moved to Audit Trail.")
            st.balloons()
            st.rerun()