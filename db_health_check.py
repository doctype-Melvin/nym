import sqlite3
import pandas as pd
import knime.scripting.io as knio

db_path = "complyable_vault.db"

def run_health_check():
    conn = sqlite3.connect(db_path)
    
    # Check if the tables actually have rows
    audit_count = pd.read_sql_query("SELECT COUNT(*) as count FROM audit_trail", conn).iloc[0]['count']
    summary_count = pd.read_sql_query("SELECT COUNT(*) as count FROM session_summary", conn).iloc[0]['count']
    
    # Pull the raw data without joining to see exactly what was saved
    audit_data = pd.read_sql_query("SELECT filepath, event_type, integrity_hash FROM audit_trail LIMIT 5", conn)
    
    conn.close()
    return audit_data, audit_count, summary_count

df, a_count, s_count = run_health_check()
# Output the audit data to the KNIME table
knio.output_tables[0] = knio.Table.from_pandas(df)
print(f"Health Check: {a_count} audit rows and {s_count} summary rows found.")