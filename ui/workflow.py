# workflow.py
import streamlit as st
import database as db
import logic
import os

# ---- DEV user_id
user_id = "DEV_DEV"

def handle_certification(current_file, raw_markdown, highlighter_df, user_id):
    """Executes the full commitment of a document to the vault."""
    
    # 1. Generate the 'Machine-View' sanitized text
    final_md = logic.generate_final_sanitized_text(raw_markdown, highlighter_df)
    
    # 2. Calculate batch confidence
    avg_conf = highlighter_df['confidence_score'].mean() if not highlighter_df.empty else 1.0
    
    # 3. Commit to the 'final_commit' table and clear workspace
    db.certify_document(
        filepath=current_file,
        original_text=raw_markdown,
        sanitized_text=final_md,
        avg_confidence=avg_conf,
        user_id=user_id
    )
    
    # 4. Success feedback
    st.toast(f"Document Certified: {os.path.basename(current_file)}", icon="✅")

def move_next():
    """Increments the document index safely."""
    if st.session_state.doc_index < st.session_state.total_files - 1:
        st.session_state.doc_index += 1
    else:
        st.session_state.batch_complete = True

def move_back():
    """Decrements the document index safely."""
    if st.session_state.doc_index > 0:
        st.session_state.doc_index -= 1