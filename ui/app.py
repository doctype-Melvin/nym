import streamlit as st
import pandas as pd
import sqlite3
import os

# Basic Page Config
st.set_page_config(page_title="Complyable | Review Portal", layout="wide")

st.title("🛡️ Complyable Review Portal")
st.subheader("Candidate Redaction Audit")

# 1. Connect to your SQLite DB (Adjust path as needed)
def get_data():
    db_path = '/Users/webdev/Documents/Complyable/Complyable Iso/complyable_vault.db'
    if not os.path.exists(db_path):
        return f"CRITICAL: Database file not found at {db_path}"
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        filepath, 
        content, 
        output_final, 
        status 
    FROM pending_review
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

try:
    df = get_data()

    # 2. Sidebar List of Candidates
    st.sidebar.header("Pending Reviews")
    selected_file = st.sidebar.selectbox("Select a document to review:", df['filepath'].tolist())

    # 3. Filter data for the selected file
    current_doc = df[df['filepath'] == selected_file].iloc[0]

    # 4. Side-by-Side View
    col1, col2 = st.columns(2)

    with col1:
        st.info("### Original Extraction (Docling)")
        # We allow the user to edit the text directly!
        edited_text = st.text_area("Audit/Edit content here:", 
                                   value=current_doc['output_final'], 
                                   height=600)

    with col2:
        st.success("### Redaction Preview")
        # Here we would normally call your Neutralizer script
        # For now, let's just show a placeholder
        st.markdown(f"**Layout Risk Score:** `{current_doc['status']}`")
        st.markdown("---")
        st.markdown(edited_text.replace("Name", "[REDACTED]")) # Simple preview logic

    # 5. Action Buttons
    if st.button("✅ Approve & Commit to Database"):
        st.balloons()
        st.write(f"Committing {selected_file} to final audit trail...")

except Exception as e:
    st.error(f"Waiting for database... Ensure your KNIME workflow has run! Error: {e}")