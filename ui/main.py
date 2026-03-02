import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components

# Import our custom modules
import database as db
import logic
from styles import inject_custom_css # We'll create this small one next

# 1. SETUP
st.set_page_config(page_title="Complyable | Review Portal", layout="wide")
inject_custom_css() # Keeps your UI professional
db.init_db_schema()

# Paths for the custom JS component
CURRENT_DIR = Path(__file__).parent.absolute()
overlayer = components.declare_component("overlayer", path=str(CURRENT_DIR / "overlay"))

# 2. STATE MANAGEMENT
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Dashboard"
if "last_click_id" not in st.session_state:
    st.session_state.last_click_id = None
if "editing_pii_id" not in st.session_state:
    st.session_state.editing_pii_id = None

# 3. SIDEBAR NAVIGATION
with st.sidebar:
    st.title("🛡️ Complyable")
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.app_mode = "Dashboard"
    if st.button("✍️ Review Station", use_container_width=True):
        st.session_state.app_mode = "Review"
    st.divider()

# 4. VIEW LOGIC
if st.session_state.app_mode == "Dashboard":
    st.header("📊 Compliance Dashboard")
    
    # Upload Section
    with st.expander("📂 Upload Documents", expanded=True):
        files = st.file_uploader("Drop PDFs/Markdown", accept_multiple_files=True)
        if files:
            # Handle upload logic...
            st.success("Files uploaded. Trigger KNIME to begin analysis.")

    # Simple Metrics
    df_pending = db.get_pending_data()
    st.metric("Pending Reviews", len(df_pending))

elif st.session_state.app_mode == "Review":
    df_pending = db.get_pending_data()
    
    if df_pending.empty:
        st.success("All caught up! No documents pending review.")
    else:
        file_list = df_pending['filepath'].tolist()
        selected_file = st.sidebar.selectbox("Active Document", file_list)
        
        # UI RENDER
        highlighter_df = db.get_detected_data(selected_file)
        doc_row = df_pending[df_pending['filepath'] == selected_file].iloc[0]
        
        st.subheader(f"Reviewing: {Path(selected_file).name}")
        
        # Side-by-Side Review
        col_main, col_preview = st.columns([2, 1])
        
        with col_main:
            rendered_html = logic.apply_overlay(doc_row['markdown'], highlighter_df)
            js_response = overlayer(markdown=rendered_html, key=f"ov_{selected_file}", height=700)

            # Interaction logic
            if js_response:
                action = js_response.get("action")
                current_click_id = js_response.get("click_id")

                if current_click_id != st.session_state.last_click_id:
                    st.session_state.last_click_id = current_click_id

                    if action == "manual_mark":
                        st.session_state.selected_word = js_response.get("word")
                        st.rerun()
                    
                    elif action == "toggle":
                        db.update_pii_status(js_response.get('pii_id'))
                        st.rerun()

        with col_preview:
            # Set context in sidebar panel
            if "selected_word" in st.session_state and st.session_state.selected_word:
                st.info(f"Selected: **{st.session_state.selected_word}**")

                choice = st.radio("Action", ["🏷️ Label", "✨ Neutralize (Gender)"])

                if choice == "🏷️ Label":
                    label = st.selectbox("Type: ", ["PERSON", "ADRESSE", "E-MAIL", "TELEFON", "PLZ", "ORT", "WEB"])
                    if st.button("Add label"):
                        # Feed into occurence index
                        word = st.session_state.selected_word
                        pii_hash = logic.create_pii_hash(word)

                        idx = doc_row['markdown'].count(word)
                        db.save_manual_tag(selected_file, word, label, idx, pii_hash)
                        st.session_state.selected_word = None
                        st.rerun()
                
                else: # Neutralize phrase
                    neutral = st.text_input("Neutrale Formulierung:", placeholder="z.B. ergebnisorientierte Vertriebsfachkraft, ")
                    if st.button("Formulierung hinzufügen"):
                        st.session_state.selected_word = None
                        st.rerun()
                
                if st.button("Cancel"):
                    st.session_state.selected_word = None
                    st.rerun()

            st.caption("🛡️ Live Redaction Preview")
            redacted = logic.generate_live_redaction(doc_row['markdown'], highlighter_df)
            st.markdown(redacted)