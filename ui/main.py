import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import sys
import unicodedata

# Link the base directory
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Highlighter function
def highlight_text(text, events):

    if not events:
        return text
    
    sorted_events = sorted(events, key=lambda x: x.get('Start', 0), reverse=True)

    highlighted = text
    for event in sorted_events:
        start = event.get('Start', 0)
        end = event.get('End', 0)

        color = '#ffcdd2' if event['Event_type'] == 'Redaction' else \
                '#bbdefb' if event['Event_type'] == 'Neutralization' else '#fff9c4'
        
        prefix = highlighted[:start]
        target = highlighted[start:end]
        suffix = highlighted[end:]

        highlighted = f"{prefix}<mark style='background-color: {color}; border-radius: 3px; padding: 0 2px;'>{target}</mark>{suffix}"

    return highlighted

# Query audit events table
def get_audit_events(filepath):
    with sqlite3.connect(DB_PATH) as conn:
        query = """
            SELECT event_type, start, end, description
            FROM audit_trail
            WHERE filepath = ?
            AND start IS NOT NULL
            AND end IS NOT NULL
        """

        events_df = pd.read_sql(query, conn, params=(filepath,))

        events_list = []
        for _, row in events_df.iterrows():
            events_list.append({
                'Event_type': row['event_type'],
                'Start': row['start'],
                'End': row['end'],
                'Description': row['description']
            })
        
        return events_list

from engine.engine import apply_neutralizer
DB_PATH = BASE_DIR / "data" / "vault" / "complyable_vault.db"
st.set_page_config(page_title="Complyable | Compliance Review", layout="wide")

def get_pending_data():
    with sqlite3.connect(DB_PATH) as conn:
        query = "Select filepath, content, output_final, status FROM pending_review WHERE status = 'PENDING'"
        return pd.read_sql(query, conn)
    
st.title("Shield Complyable | Recruiter Review Portal")
st.markdown("Review Complyable's output and add your own changes")

df_pending = get_pending_data()

if df_pending.empty:
    st.success("No pending reviews. Everything is safe for AI use.")
else: 
    st.sidebar.header("Files to review")
    selected_file = st.sidebar.selectbox("Select a Document", df_pending['filepath'].tolist())

    row = df_pending[df_pending['filepath'] == selected_file].iloc[0]

    # unicode normalization
    raw_content = unicodedata.normalize('NFC', row['content'])
    raw_output = unicodedata.normalize('NFC', row['output_final'])

    audit_events = get_audit_events(selected_file)

    col1, col2 = st.columns(2)

    with col1: 
        st.subheader("Original content (with detections)")
        st.info("PII already removed by Tier 1, 2 & 3")
        html_original = highlight_text(raw_content, audit_events)
        st.markdown(f"<div style='background-color: #f9f9f9-; padding: 15px; border-radius: 5px; font-family: sans-serif;'>{html_original}</div>", unsafe_allow_html=True)
        #st.text_area("Source Content", row['content'], height=600, disabled=True)

    
    with col2:
        st.subheader("Finalized (AI Ready)")
        st.text_area("Edit Content", value=row['output_final'],key="editor", height=600)

    st.divider()
    c1, c2, c3 = st.columns([1,1,4])
    with c1:
        if st.button("Approve & Sign"):
            st.balloons()
    with c2:
        if st.button("Re-Neutralize"):
            st.warning("Re-running engine ...")