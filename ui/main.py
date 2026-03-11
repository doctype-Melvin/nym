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
from datetime import datetime
import pipeline


# 1. SETUP
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
if "pending_neutral" not in st.session_state:
    st.session_state.pending_neutral = None
if "confirm_discard" not in st.session_state:
    st.session_state.confirm_discard = False
if "archive_sort_asc" not in st.session_state:
    st.session_state.archive_sort_asc = False  # newest first by default
if "archive_search_audit" not in st.session_state:
    st.session_state.archive_search_audit = ""
if "upload_warnings" not in st.session_state:
    st.session_state.upload_warnings = []

# ----------------------------------------------------------------------------------------
# AUTH GATE
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

    st.stop()

# ----------------------------------------------------------------------------------------
# FILE SELECTION
# ----------------------------------------------------------------------------------------
if not file_list:
    st.session_state.doc_index = 0
    selected_file = None
else:
    if st.session_state.doc_index >= len(file_list):
        st.session_state.doc_index = 0
    selected_file = file_list[st.session_state.doc_index]

# ----------------------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------------------
with st.sidebar:
    st.title("🛡️ Complyable")
    if st.button("Dashboard", use_container_width=True):
        st.session_state.app_mode = "Dashboard"
        st.rerun()
    if st.button("Revision & Freigabe", use_container_width=True):
        st.session_state.app_mode = "Review"
        st.rerun()
    if st.button("Audit Archiv", use_container_width=True):
        st.session_state.app_mode = "Archive"
        st.rerun()
    if st.button("Output-Ordner", use_container_width=True):
        if not logic.open_folder(logic.OUTPUT_DIR):
            st.error("Ordner existiert noch nicht. Erst einen Batch abschließen!")
        host_path = logic.get_output_display_path()
        st.caption(f"📁: {host_path}")

    if st.session_state.app_mode == "Review" and selected_file:
        selected_path = st.selectbox(
            "Schnellauswahl",
            options=file_list,
            index=st.session_state.doc_index,
            format_func=lambda x: Path(x).name,
            key=f"jump_select_{len(file_list)}"
        )
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

# ----------------------------------------------------------------------------------------
# DASHBOARD VIEW
# ----------------------------------------------------------------------------------------
if st.session_state.app_mode == "Dashboard":
    is_busy = st.session_state.workflow_running

    if is_busy:
        st.warning("Workflow läuft. Bitte warten.")

    st.header("Dashboard")

    pending_count = len(db.get_pending_data())
    ready_count = len(workflow.get_clipboard_stack())

    col_m1, col_m2 = st.columns(2)
    col_m1.metric("📄 Zu prüfen", pending_count)
    col_m2.metric("✅ Geprüft", ready_count)

    if st.session_state.workflow_running:
        with st.spinner("Pipeline läuft... Bitte warten"):
            success, message = logic.trigger_pipeline(str(logic.INPUT_DIR))
            st.session_state.workflow_running = False
            if success:
                st.session_state.uploader_key += 1
                st.session_state.app_mode = "Review"
                st.session_state.doc_index = 0
                st.toast("Verarbeitung abgeschlossen!")
            else:
                st.error(f"Fehler {message}")
                st.code(message)
            st.rerun()

    # ── Ready documents list ──
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
            highlighter_df = db.get_detected_data(filepath)
            audit_id = logic.create_pii_hash(filename)[:8]
            sanitized_text = logic.generate_final_sanitized_text(md_content, highlighter_df)
            final_clip = f"{sanitized_text}\n\n--- Complyable Audit ID: {audit_id} ---"

            row_cols = st.columns([4, 1, 1, 1])
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
            with row_cols[3]:
                if st.button("Verwerfen", key=f"discard_{audit_id}", help="Dokument verwerfen"):
                    db.discard_document(filepath, st.session_state.current_user['username'])
                    st.rerun()

    # ── Discarded documents list ──
    discarded_docs = db.get_discarded_documents()
    if not discarded_docs.empty:
        st.divider()
        with st.expander(f"🗑️ Verworfene Dokumente ({len(discarded_docs)})"):
            for _, row in discarded_docs.iterrows():
                filepath = row['filepath']
                filename = Path(filepath).name
                dis_cols = st.columns([4, 1])
                with dis_cols[0]:
                    st.caption(filename)
                with dis_cols[1]:
                    if st.button("↩️ Wiederherstellen", key=f"restore_{filename}"):
                        db.restore_document(
                            filepath,
                            st.session_state.current_user['username']
                        )
                        st.session_state.app_mode = "Review"
                        st.rerun()

# ----------------------------------------------------------------------------------------
# REVIEW VIEW
# ----------------------------------------------------------------------------------------
elif st.session_state.app_mode == "Review":
    is_busy = st.session_state.workflow_running

    st.header("Revision & Freigabe")

    if is_busy:
        st.warning("Workflow läuft. Bitte warten.")

    if st.session_state.workflow_running:
        with st.spinner("Pipeline läuft... Bitte warten"):
            success, message = logic.trigger_pipeline(str(logic.INPUT_DIR))
            st.session_state.workflow_running = False
            if success:
                st.session_state.uploader_key += 1
                st.session_state.doc_index = 0
                st.toast("Verarbeitung abgeschlossen!")
            else:
                st.error(f"Fehler {message}")
                st.code(message)
            st.rerun()

    # ── Uploader always visible ──
    uploaded_files = st.file_uploader(
        "Neue Dokumente ablegen",
        accept_multiple_files=True,
        disabled=is_busy,
        key=f"uploader_main_{st.session_state.uploader_key}"
    )
    
    if uploaded_files and not is_busy:
        if st.button("Prozess starten", disabled=is_busy):
            duplicates = []
            staged = []
            for file in uploaded_files:
                result = logic.stage_uploaded_file(file)
                if result['duplicate']:
                    duplicates.append(result)
                else:
                    staged.append(result)

            if duplicates:
                st.session_state.upload_warnings = duplicates

            if staged:
                st.session_state.workflow_running = True
                
                st.rerun()
            else:
                st.rerun()

    # Show persistent duplicate warnings above uploader
    if st.session_state.upload_warnings:
        for d in st.session_state.upload_warnings:
            location_label = "Archiv" if d['location'] == 'archive' else "Warteschlange"
            st.warning(
                f"**{d['filename']}** wurde bereits verarbeitet "
                f"({location_label} — Audit ID: `{d['audit_id']}`). "
                f"Datei wird übersprungen."
            )
        if st.button("✖️ Meldungen schließen", key="clear_warnings"):
            st.session_state.upload_warnings = []
            st.rerun()

    # ── Review editor — only if documents are pending ──
    if not file_list:
        st.info("Keine Dokumente zur Prüfung. Bitte Dateien ablegen.")
    else:
        current_rows = df_pending[df_pending['filepath'] == selected_file]
        if current_rows.empty:
            st.session_state.doc_index = 0
            st.rerun()
            st.stop()

        doc_row = current_rows.iloc[0]
        highlighter_df = db.get_detected_data(selected_file)
        # ... rest of review editor unchanged

        # ── Navigation bar ──
        nav_prev, nav_status, nav_next, nav_discard = st.columns([1, 2, 1, 1])

        with nav_prev:
            if st.button("⬅️ Zurück", disabled=(not st.session_state.last_ready_file)):
                if st.session_state.last_ready_file:
                    workflow.mark_document_ready(st.session_state.last_ready_file, 'PENDING')
                    st.session_state.last_ready_file = None
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
                st.toast("Dokument ist bereinigt!")
                st.rerun()

        with nav_discard:
            if not st.session_state.confirm_discard:
                if st.button("🗑️ Verwerfen", use_container_width=True, key="discard_btn"):
                    st.session_state.confirm_discard = True
                    st.rerun()
            else:
                st.warning("Wirklich verwerfen?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Ja", use_container_width=True, key="confirm_yes"):
                        db.discard_document(
                            selected_file,
                            st.session_state.current_user['username']
                        )
                        st.session_state.confirm_discard = False
                        st.session_state.selected_word = None
                        st.session_state.doc_index = 0
                        st.rerun()
                with col_no:
                    if st.button("Nein", use_container_width=True, key="confirm_no"):
                        st.session_state.confirm_discard = False
                        st.rerun()

        # ── Review edit area ──
        col_main, col_toolbox = st.columns([3, 1])

        with col_main:
            rendered_html = logic.apply_overlay(doc_row['markdown'], highlighter_df)
            js_response = overlayer(markdown=rendered_html, key=f"ov_{selected_file}", height=700)

            if js_response:
                action = js_response.get("action")
                current_click_id = js_response.get("click_id")

                if current_click_id != st.session_state.last_click_id:
                    st.session_state.last_click_id = current_click_id
                    st.session_state.selected_word = js_response.get("word")
                    st.session_state.selected_id = js_response.get("pii_id")
                    st.session_state.confirm_discard = False  # reset discard on new interaction

                    if action == "toggle":
                        db.toggle_pii_status(st.session_state.selected_id)
                        st.rerun()
                    else:
                        # "select" (gender) or "manual_mark"
                        st.rerun()

        with col_toolbox:
            grab_state = st.session_state.get("selected_word")
            word = logic.strip_ui_labels(grab_state)
            target_id = st.session_state.get("selected_id")
            st.caption(f"grab: {grab_state} | word: {word} | id: {target_id}")
            if word:
                if target_id is not None:
                    details = db.get_pii_details(target_id)

                    if details is None:
                        st.session_state.selected_word = None
                        st.session_state.selected_id = None

                    elif details['event_code'] in ('USR-GIP', 'T3-GIP'):
                        # ── Edit existing neutral phrase ──
                        st.info(f"Ersetzen: **{word}**")
                        updated = st.text_input(
                            "Formulierung bearbeiten:",
                            value=details['neutral_phrase'],
                            key=f"edit_neutral_{word}"
                        )
                        if st.button("💾 Speichern", use_container_width=True, key="save_edit"):
                            if updated:
                                db.update_neutralization(
                                    selected_file, word,
                                    details['neutral_phrase'], updated
                                )
                                st.session_state.selected_word = None
                                st.rerun()
                        if st.button("↩️ Eingabe entfernen", use_container_width=True, key="revert_neutral"):
                            db.revert_neutralization(selected_file, details['pii_text'])
                            st.session_state.selected_word = None
                            st.session_state.selected_id = None
                            st.rerun()
                        if st.button("Cancel", key="cancel_edit", use_container_width=True):
                            st.session_state.selected_word = None
                            st.rerun()

                    elif details['category'] == 'GEN-FL':
                        # ── New neutral phrase for flagged word ──
                        st.info(f"Markiert: **{word}**")
                        neutral = st.text_input(
                            "Neutrale Formulierung:",
                            placeholder="z.B. Fachkraft",
                            key=f"neutral_input_{word}"
                        )
                        if st.button("💾 Speichern", use_container_width=True, key="save_genfl"):
                            if neutral:
                                db.save_neutralization(selected_file, word, neutral)
                                st.session_state.selected_word = None
                                st.rerun()
                        if st.button("Cancel", key="cancel_genfl", use_container_width=True):
                            st.session_state.selected_word = None
                            st.rerun()

                    else:
                        # ── PII sync logic ──
                        others_count = db.get_unsynced_count(
                            selected_file, word, details['status']
                        )
                        if others_count > 0:
                            st.info(f"Target: **{word}**")
                            btn_label = "🚫 Exclude all" if details['status'] == "EXCLUDE" \
                                        else "✅ Redact all"
                            if st.button(f"{btn_label} ({others_count + 1})",
                                        use_container_width=True, key="sync_btn"):
                                db.sync_all_pii_status(selected_file, word, details['status'])
                                st.rerun()
                            st.divider()
                            if st.button("Cancel", key="cancel_sync", use_container_width=True):
                                st.session_state.selected_word = None
                                st.rerun()
                        else:
                            st.session_state.selected_word = None
                            st.session_state.selected_id = None

                else:
                    # ── Manual selection — no existing pii_id ──

                    choice = st.radio("Action", ["🏷️ Label", "✨ Neutralize (Gender)"])
                    st.info(f"Markiert: **{word}**")

                    if choice == "🏷️ Label":
                        label = st.selectbox("Type: ", [
                            "PERSON", "ADRESSE", "E-MAIL",
                            "TELEFON", "PLZ", "ORT", "WEB"
                        ])
                        if st.button("Add label", use_container_width=True, key="add_label"):
                            pii_hash = logic.create_pii_hash(word)
                            idx = doc_row['markdown'].count(word)
                            db.save_manual_tag(selected_file, word, label, idx, pii_hash)
                            st.session_state.selected_word = None
                            st.rerun()
                    else:
                        neutral = st.text_input(
                            "Neutrale Formulierung:",
                            placeholder="z.B. Fachkraft",
                            key=f"neutral_input_manual_{word}"
                        )
                        if st.button("💾 Speichern", use_container_width=True, key="save_manual"):
                            if neutral:
                                db.save_neutralization(selected_file, word, neutral)
                                st.session_state.selected_word = None
                                st.rerun()
                    if st.button("Abbrechen", key="cancel_manual", use_container_width=True):
                        st.session_state.selected_word = None
                        st.rerun()
elif st.session_state.app_mode == "Archive":
    st.header("Audit Archiv")

    archived = db.get_archived_documents()

    if archived.empty:
        st.info("Noch keine archivierten Dokumente.")
    else:
        # ── Summary metrics ──
        col_a1, col_a2, col_a3 = st.columns(3)
        col_a1.metric("Archivierte Dokumente", len(archived))
        #col_a2.metric("👤 Bearbeitet von", archived['user_id'].nunique())
        col_a2.metric("", "")
        col_a3.metric("Ältester Eintrag", archived['approval_timestamp'].min()[:10])

        # ── Search, sort and clear ──
        col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
        with col_s1:
            search_audit = st.text_input(
                "Audit ID suchen",
                value=st.session_state.archive_search_audit,
                placeholder="z.B. A3F2B1C0",
                key="audit_search_input"
            )
            st.session_state.archive_search_audit = search_audit
        with col_s2:
            sort_label = "📅 Älteste zuerst" if not st.session_state.archive_sort_asc \
                        else "📅 Neueste zuerst"
            if st.button(sort_label, use_container_width=True):
                st.session_state.archive_sort_asc = not st.session_state.archive_sort_asc
                st.rerun()
        with col_s3:
            if st.button("✖️ Zurücksetzen", use_container_width=True):
                st.session_state.archive_search_audit = ""
                st.session_state.archive_sort_asc = False
                st.rerun()

        # ── Apply filter and sort ──
        filtered = archived.copy()
        if search_audit:
            filtered = filtered[
                filtered['audit_id'].str.contains(search_audit, case=False, na=False)
            ]
        filtered = filtered.sort_values(
            by='approval_timestamp',
            ascending=st.session_state.archive_sort_asc
        )

        if search_audit or st.session_state.archive_sort_asc:
            st.caption(f"{len(filtered)} Einträge gefunden")
        st.divider()

        # ── Export button ──
        if st.button("📥 Audit-Daten exportieren", use_container_width=True):
            try:
                export_path = db.export_audit_xlsx(
                    os.getenv('HOST_OUTPUT_PATH', str(logic.OUTPUT_DIR))
                )
                with open(export_path, 'rb') as f:
                    st.download_button(
                        label="💾 Excel herunterladen",
                        data=f,
                        file_name=Path(export_path).name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_audit_archive"
                    )
                st.success(f"Exportiert nach: {export_path}")
            except Exception as e:
                st.error(f"Export fehlgeschlagen: {e}")

        st.divider()

        # ── Document rows ──
        cols = st.columns([3, 1, 1])
        cols[0].write('**Audit ID**')
        cols[1].write('**Datum**')
        cols[2].write('**Aktionen**')

        for _, row in filtered.iterrows():
            audit_id = row['audit_id']
            timestamp = datetime.strptime(str(row['approval_timestamp'])[:16], "%Y-%m-%dT%H:%M").strftime("%d.%m.%Y %H:%M")
            sanitized = row['sanitized_text'] or ""
            final_clip = f"{sanitized}\n\n--- Complyable Audit ID: {audit_id} ---"

            row_cols = st.columns([3, 1, 1])
            with row_cols[0]:
                with st.expander(f"{audit_id}"):
                    st.text_area(
                        "Vorschau",
                        sanitized,
                        height=300,
                        disabled=True,
                        key=f"archive_area_{row['commit_uuid']}"
                    )
            with row_cols[1]:
                st.caption(timestamp)
            with row_cols[2]:
                copy_button(
                    final_clip,
                    icon='st',
                    copied_label="Kopiert!",
                    key=f"archive_copy_{row['commit_uuid']}"
                )