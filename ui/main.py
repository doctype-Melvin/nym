import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components
import database as db
import logic
import workflow
from styles import inject_custom_css
from st_copy import copy_button
import os
import shutil


# 1. SETUP (Only one set_page_config allowed, and it must be first)
st.set_page_config(page_title="Complyable | Review Portal", layout="wide")
inject_custom_css() 
db.init_db_schema()

# Paths for the custom JS component
CURRENT_DIR = Path(__file__).parent.absolute()
overlayer = components.declare_component("overlayer", path=str(CURRENT_DIR / "overlay"))

df_pending = db.get_pending_data()
file_list = df_pending['filepath'].tolist()
# 2. STATE MANAGEMENT
if "pending_jump" in st.session_state and st.session_state.pending_jump:
    target = st.session_state.pending_jump
    if target in file_list:
        st.session_state.doc_index = file_list.index(target)
    st.session_state.pending_jump = None
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Dashboard"
if "last_click_id" not in st.session_state:
    st.session_state.last_click_id = None
if "selected_word" not in st.session_state:
    st.session_state.selected_word = None
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None
if "doc_index" not in st.session_state:
    st.session_state.doc_index = 0
if "total_files" not in st.session_state:
    st.session_state.total_files = len(file_list) 
else:
    st.session_state.total_files = len(file_list)
if "batch_complete" not in st.session_state:
    st.session_state.batch_complete = False
if "last_ready_file" not in st.session_state:
    st.session_state.last_ready_file = None
if "workflow_running" not in st.session_state:
    st.session_state.workflow_running = False
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ----------------------------------------------------------------------------------------
if not st.session_state.authenticated:
    st.title("🛡️ Complyable")
    st.subheader("Bitte anmelden")
    
    no_users = db.user_count() == 0
    
    if no_users:
        st.info("Willkommen! Bitte erstellen Sie den ersten Benutzer.")
        st.subheader("Benutzer anlegen")
        new_username = st.text_input("Benutzername", key="reg_user")
        new_password = st.text_input("Passwort", type="password", key="reg_pass")
        new_password2 = st.text_input("Passwort bestätigen", type="password", key="reg_pass2")
        
        if st.button("Benutzer erstellen", type="primary"):
            if not new_username or not new_password:
                st.error("Bitte alle Felder ausfüllen.")
            elif new_password != new_password2:
                st.error("Passwörter stimmen nicht überein.")
            else:
                if db.create_user(new_username, new_password, role='admin'):
                    st.success("Benutzer erstellt! Bitte jetzt anmelden.")
                    st.rerun()
                else:
                    st.error("Benutzername bereits vergeben.")
    else:
        username = st.text_input("Benutzername", key="login_user")
        password = st.text_input("Passwort", type="password", key="login_pass")
        
        if st.button("Anmelden", type="primary"):
            user = db.verify_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("Ungültige Anmeldedaten.")
    
    st.stop()  # ← blocks entire rest of app if not authenticated
# ----------------------------------------------------------------------------------------

if not file_list:
    st.session_state.doc_index = 0
    selected_file = None
else:
    # If the index is out of bounds (which shouldn't happen now), reset it
    if st.session_state.doc_index >= len(file_list):
        st.session_state.doc_index = 0
    
    selected_file = file_list[st.session_state.doc_index]
    
#selected_file = file_list[st.session_state.doc_index] if file_list else None

# 3. SIDEBAR NAVIGATION (Global Actions)
with st.sidebar:
    st.title("🛡️ Complyable")
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.app_mode = "Dashboard"
        st.rerun()
    if st.button("✍️ Review Station", use_container_width=True):
        st.session_state.app_mode = "Review"
        st.rerun()
    if st.button("📁 Output-Ordner öffnen", use_container_width=True):
        if not logic.open_folder(logic.OUTPUT_DIR):
            st.error("Ordner existiert noch nicht. Erst einen Batch abschließen!")

    st.caption(f"Speicherort: {logic.OUTPUT_DIR.name}")
    # We move the file selection here to keep the main area for the editor
    if st.session_state.app_mode == "Review" and selected_file:

        selected_path = st.selectbox(
            "Schnellauswahl", 
            options=file_list, 
            index=st.session_state.doc_index,
            format_func=lambda x: Path(x).name,
            key=f"jump_select_{len(file_list)}" # Adding an explicit key helps Streamlit track state
        )
    
        # Update the global doc_index based on the new selection
        new_index = file_list.index(selected_path)
        if new_index != st.session_state.doc_index:
            st.session_state.doc_index = new_index
            st.rerun()

    st.divider()
    st.sidebar.markdown("<br>" * 10, unsafe_allow_html=True)

    if st.session_state.current_user:
        st.caption(f"👤 {st.session_state.current_user['username']}")
        if st.button("Abmelden", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()
# 4. VIEW LOGIC
if st.session_state.app_mode == "Dashboard":
    is_busy = st.session_state.workflow_running

    if is_busy:
        st.warning("Workflow läuft. Bitte warten.")
    
    st.header("📊 Dashboard")

    pending_count = len(db.get_pending_data())
    ready_count = len(workflow.get_clipboard_stack())
    
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("📄 Zu prüfen", pending_count)
    col_m2.metric("✅ Geprüft", ready_count)

    uploaded_files = st.file_uploader(
            "Neue Dokumente ablegen",
            accept_multiple_files = True,
            disabled=is_busy,
            key=f"uploader_main_{st.session_state.uploader_key}"
        )

    if uploaded_files and not is_busy:
        if st.button("Prozess starten", disabled=is_busy):
            for file in uploaded_files if uploaded_files else []:
                logic.stage_uploaded_file(file)                    
            st.session_state.workflow_running = True
            st.rerun()

    if st.session_state.workflow_running:
        with st.spinner("Pipeline läuft... Bitte warten"):
            success, message = logic.trigger_pipeline(str(logic.INPUT_DIR))
            st.session_state.workflow_running = False
            if success:
                st.session_state.uploader_key +=1
                st.session_state.app_mode = "Review"
                st.session_state.doc_index = 0
                st.toast("Verarbeitung abgeschlossen!")
            else:
                st.error(f"Fehler {message}")
                st.code(message)
            st.rerun()

    ready_docs = workflow.get_clipboard_stack()

    if not ready_docs:
        st.info("Liste geprüfter Dokumente ist leer.")
    else: 
        if st.button("📦 Alle archivieren", type="primary", key='top'):
                with st.spinner("Zertifikate werden generiert..."):
                    success = workflow.archive_ready_batch(
                        user_id=st.session_state.current_user['user_id']
                    )
                    if success:
                        st.success("Batch erfolgreich archiviert! Zertifikate liegen im Zielordner")
                        st.rerun()
                    else: 
                        st.warning("Keine Dokumente zum Archivieren gefunden.")
        cols = st.columns([3, 1, 1, 1])
        cols[0].write('**Datei**')
        cols[2].write('**Aktionen**')

        for filepath, md_content in ready_docs:
            filename = Path(filepath).name
            
            # 1. Fetch data for this specific file
            highlighter_df = db.get_detected_data(filepath)
            audit_id = logic.create_pii_hash(filename)[:8]
            
            # 2. Generate the preview text
            sanitized_text = logic.generate_final_sanitized_text(md_content, highlighter_df)
            final_clip = f"{sanitized_text}\n\n--- Complyable Audit ID: {audit_id} ---"      

            row_cols = st.columns([4, 1, 1])
            # 3. Wrap the row in an Expander
            with row_cols[0]:
                with st.expander(f"{filename} | Audit ID: {audit_id}"):
                    st.text_area("Vorschau", sanitized_text, height=500, disabled=True, key=f"area_{filename}")
                
            with row_cols[1]:
                copy_button(final_clip, icon='st', copied_label="Kopiert!", key=f"copy_{filename}")

            with row_cols[2]:
                if st.button("Überarbeiten", key=f"revert_{audit_id}"):
                    workflow.mark_document_ready(filepath, 'PENDING')
                    st.session_state.app_mode = "Review"
                    st.session_state.pending_jump = filepath
                    st.rerun()

elif st.session_state.app_mode == "Review":
    is_busy = st.session_state.workflow_running

    if is_busy:
        st.warning("Workflow läuft. Bitte warten.")  
    if not file_list:
        st.info("✨ **Alle Dokumente sind geprüft!**")
    
    else: 
        current_rows = df_pending[df_pending['filepath'] == selected_file] 

        if current_rows.empty:
            st.session_state.doc_index = 0
            st.rerun()
            st.stop()

        doc_row = current_rows.iloc[0]
        highlighter_df = db.get_detected_data(selected_file)
            
            
        nav_prev, nav_status, nav_next = st.columns([1, 2, 1])

        with nav_prev:
            if st.button("⬅️ Zurück", disabled=(not st.session_state.last_ready_file)):
                if st.session_state.last_ready_file:
                    workflow.mark_document_ready(st.session_state.last_ready_file, 'PENDING')
                    st.session_state.last_ready_file = None
                #workflow.move_back()
                st.rerun()

        with nav_status:
            st.markdown(f"**Dokument {st.session_state.doc_index + 1} / {st.session_state.total_files}**")

        with nav_next:
            if st.button("✅ Bereinigt", type="primary"):
                st.session_state.last_ready_file = selected_file
                workflow.mark_document_ready(selected_file, 'READY')
                st.session_state.doc_index = 0

                if len(file_list) <= 1:
                    st.session_state.app_mode = "Dashboard"
                    st.toast("All documents reviewed!")
                # else:
                #     st.session_state.doc_index = 0
                #     st.session_state.app_mode = "Dashboard"
                #     st.toast("Alles bereinigt!")
                st.toast("Dokument ist bereinigt!")
                st.rerun()

        col_main, col_toolbox = st.columns([3, 1])
        with col_main:
            rendered_html = logic.apply_overlay(doc_row['markdown'], highlighter_df)
            js_response = overlayer(markdown=rendered_html, key=f"ov_{selected_file}", height=700)

            # --- YOUR WORKING INTERACTION LOGIC ---
            if js_response:
                action = js_response.get("action")
                current_click_id = js_response.get("click_id")

                if current_click_id != st.session_state.last_click_id:
                    st.session_state.last_click_id = current_click_id
                    # Store the ID and Word so the toolbox can see them
                    st.session_state.selected_word = js_response.get("word")
                    st.session_state.selected_id = js_response.get("pii_id")

                    if action == "toggle":
                        db.toggle_pii_status(st.session_state.selected_id)
                        st.rerun()
                    else:
                        st.rerun()

        with col_toolbox:
            grab_state = st.session_state.get("selected_word")
            word = logic.strip_ui_labels(grab_state)
            target_id = st.session_state.get("selected_id")
            
            if word: 

                # 1. Sync Logic (Only for existing detections)
                if target_id is not None:
                    current_status = db.get_pii_status(target_id)
                    others_count = db.get_unsynced_count(selected_file, word, current_status)

                    if others_count > 0:
                        st.info(f"Target: **{word}**")
                        btn_label = "🚫 Exclude all" if current_status == "EXCLUDE" else "✅ Redact all"
                        # Only rerun IF the button is pressed
                        if st.button(f"{btn_label} ({others_count + 1})", use_container_width=True):
                            db.sync_all_pii_status(selected_file, word, current_status)
                            st.rerun()
                        
                        st.divider()
                        if st.button("Cancel", use_container_width=True):
                            st.session_state.selected_word = None
                            st.rerun()
                    
                    else: 
                        st.session_state.selected_word = None
                        st.session_state.selected_id = None

                else:
                # 2. Label/Neutralize Logic (Always visible if a word is selected)
                    choice = st.radio("Action", ["🏷️ Label", "✨ Neutralize (Gender)"])

                    if choice == "🏷️ Label":
                        label = st.selectbox("Type: ", ["PERSON", "ADRESSE", "E-MAIL", "TELEFON", "PLZ", "ORT", "WEB"])
                        if st.button("Add label", use_container_width=True):
                            pii_hash = logic.create_pii_hash(word)
                            idx = doc_row['markdown'].count(word)
                            db.save_manual_tag(selected_file, word, label, idx, pii_hash)
                            st.session_state.selected_word = None
                            st.rerun()
                    
                    else: # Neutralize phrase
                        neutral = st.text_input("Neutrale Formulierung:", placeholder="z.B. Fachkraft")
                        if st.button("Formulierung hinzufügen", use_container_width=True):
                            db.save_neutralization(selected_file, word, neutral) 
                            st.session_state.selected_word = None
                            st.rerun()
                    
                    if st.button("Cancel", use_container_width=True):
                            st.session_state.selected_word = None
                            st.rerun()