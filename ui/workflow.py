# workflow.py
import streamlit as st
import database as db
import logic
import os
from datetime import datetime

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

def mark_document_ready(filepath, status):
    db.mark_as_ready(filepath, status)

def get_clipboard_stack():
    return db.get_ready_for_clipboard()

def archive_ready_batch(user_id = "Admin"):
    ready_docs = db.get_ready_for_clipboard() # Returns [(path, md), ...]
    
    if not ready_docs:
        return False
    
    batch_timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    batch_folder_name = f"Batch_{batch_timestamp}"
    batch_path = logic.OUTPUT_DIR / batch_folder_name
    batch_path.mkdir(parents=True, exist_ok=True)

    for filepath, md_content in ready_docs:
        filename = os.path.basename(filepath)
        highlighter_df = db.get_detected_data(filepath)
        sanitized_text = logic.generate_final_sanitized_text(md_content, highlighter_df)
        avg_conf = highlighter_df['confidence_score'].mean() if not highlighter_df.empty else 1.0
        audit_id = logic.create_pii_hash(filepath)[:8]
        
        cert_filename = f"CERT_{audit_id}_{filename.replace('.pdf', '')}.pdf"
        logic.generate_pdf_certificate(filepath, user_id, audit_id, save_path=batch_path / cert_filename)

        redact_filename = f"RED_{audit_id}_{filename.replace('.pdf', '')}.pdf"
        logic.generate_redacted_pdf(sanitized_text, save_path=batch_path / redact_filename)
        
        db.certify_document(
            filepath=filepath,
            original_text=md_content,
            sanitized_text=sanitized_text,
            avg_confidence=avg_conf,
            user_id=user_id
        )

    return True