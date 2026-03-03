import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components
import database as db
import logic
import workflow
from styles import inject_custom_css

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

selected_file = file_list[st.session_state.doc_index] if file_list else None

# 3. SIDEBAR NAVIGATION (Global Actions)
with st.sidebar:
    st.title("🛡️ Complyable")
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.app_mode = "Dashboard"
        st.rerun()
    if st.button("✍️ Review Station", use_container_width=True):
        st.session_state.app_mode = "Review"
        st.rerun()
    st.divider()
    
    # We move the file selection here to keep the main area for the editor
    if st.session_state.app_mode == "Review" and selected_file:
        selected_index = st.selectbox(
            "Quick Jump", 
            range(len(file_list)), 
            index=st.session_state.doc_index,
            format_func=lambda x: Path(file_list[x]).name
        )
        
        # 2. If the user picks a different file in the dropdown, update the index
        if selected_index != st.session_state.doc_index:
            st.session_state.doc_index = selected_index
            st.rerun()
        if st.button("🚀 Finalize & Export", use_container_width=True):
                st.warning("Export logic (The Endboss) goes here!")

# 4. VIEW LOGIC
if st.session_state.app_mode == "Dashboard":
    st.header("📊 Compliance Dashboard")
    # ... (Your existing upload/metrics code) ...

elif st.session_state.app_mode == "Review":    
    if not file_list:
        st.success("All caught up!")
    else:        
        highlighter_df = db.get_detected_data(selected_file)
        doc_row = df_pending[df_pending['filepath'] == selected_file].iloc[0]
        
        
        nav_prev, nav_status, nav_next = st.columns([1, 2, 1])

        with nav_prev:
            if st.button("⬅️ Back", disabled=(st.session_state.doc_index == 0)):
                workflow.move_back()
                st.rerun()

        with nav_status:
            st.markdown(f"**CV {st.session_state.doc_index + 1} / {st.session_state.total_files}**")

        with nav_next:
            if st.button("✅ CERTIFY & NEXT", type="primary"):
                # The 'Heavy Lifting' is now hidden in the workflow module
                workflow.handle_certification(selected_file, doc_row['markdown'], highlighter_df, user_id="DEV_")
                workflow.move_next()
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
            word = st.session_state.get("selected_word")
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