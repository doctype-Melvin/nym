# workflow.py
import streamlit as st
import database as db
import logic
import os
from pathlib import Path
from datetime import datetime

# ---- DEV user_id

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

def archive_ready_batch(user_id="Admin"):
    ready_docs = db.get_ready_for_clipboard()
    if not ready_docs:
        return False, "Keine Dokumente zum Archivieren gefunden."

    batch_timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    batch_path = logic.OUTPUT_DIR / f"Batch_{batch_timestamp}"
    batch_path.mkdir(parents=True, exist_ok=True)

    processed = 0
    errors = []

    for filepath, md_content in ready_docs:
        try:
            highlighter_df = db.get_detected_data(filepath)
            sanitized_text = logic.generate_final_sanitized_text(md_content, highlighter_df)
            if not sanitized_text:
                sanitized_text = md_content
            audit_id = logic.create_pii_hash(filepath)[:8]

            logic.generate_compliance_document(
                filepath=filepath,
                sanitized_text=sanitized_text,
                user_id=user_id,
                audit_id=audit_id,
                highlighter_df=highlighter_df,
                save_path=batch_path / f"{audit_id}.pdf"
            )
            db.certify_document(
                filepath=filepath,
                original_text=md_content,
                sanitized_text=sanitized_text,
                user_id=user_id
            )
            processed += 1
        except Exception as e:
            import traceback
            errors.append(f"{os.path.basename(filepath)}: {str(e)}\n{traceback.format_exc()}")

    db.purge_discarded()

    if errors:
        return False, f"{processed} archiviert, {len(errors)} Fehler:\n" + "\n".join(errors)
    return True, f"{processed} Dokumente erfolgreich archiviert."

def regenerate_certificates(commit_uuids, user_id):
    errors = []
    processed = 0
    
    for commit_uuid in commit_uuids:
        try:
            row = db.get_archived_by_commit(commit_uuid)
            if row is None:
                errors.append(f"{commit_uuid}: nicht gefunden.")
                continue
            
            highlighter_df = db.get_audit_highlighter_df(commit_uuid)
            audit_id = row['audit_id']
            
            batch_path = logic.OUTPUT_DIR / f"Regenerated_{datetime.now().strftime('%Y%m%d_%H%M')}"
            batch_path.mkdir(parents=True, exist_ok=True)
            
            logic.generate_compliance_document(
                filepath=f"[archived]",
                sanitized_text=row['sanitized_text'],
                user_id=row['user_id'],
                audit_id=audit_id,
                highlighter_df=highlighter_df,
                save_path=batch_path / f"{audit_id}.pdf"
            )
            processed += 1
        except Exception as e:
            import traceback
            errors.append(f"{commit_uuid}: {str(e)}\n{traceback.format_exc()}")
    
    if errors:
        return False, f"{processed} erstellt, {len(errors)} Fehler:\n" + "\n".join(errors)
    return True, f"{processed} Zertifikate erfolgreich erstellt."