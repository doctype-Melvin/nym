import sqlite3
import pandas as pd
import knime.scripting.io as knio

db_path = "complyable_vault.db"

def health_check():
    connect = sqlite3.connect(db_path)

    dict_check = pd.read_sql_query("SELECT * FROM job_dict LIMIT 5", connect)

    audit_check = pd.read_sql_query('''
            SELECT
                s.file_name,
                s.compliance_grade,
                a.event_type,
                a.description
                a.integrity_hash
            FROM session_summary s
            JOIN audit_trail a ON s.file_name = a.filepath
            ORDER BY s.processed_at DESC
            LIMIT 10
        ''', connect)
    
    connect.close()
    return dict_check, audit_check

dict_df, audit_df = health_check()
knio.output_tables[0] = knio.Table.from_pandas(audit_df)