import sqlite3
import pandas as pd
import knime.scripting.io as knio
from datetime import datetime
import uuid

summary_results = knio.input_tables[0].to_pandas()

db_path = "complyable_vault.db"

def db_commit(df):
    try: 
        connect = sqlite3.connect(db_path)
        cursor = connect.cursor()

        current_session_id = str(uuid.uuid4())
        processed_at = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO session_summary (
                           session_uuid,
                           file_name,
                           pii_count,
                           neutral_count,
                           trust_score,
                           compliance_grade,
                           processed_at
                           
                        )
                        Values (?, ?, ?, ?, ?, ?, ?)   
                        ''', (
                            current_session_id,
                            row["File"],
                            int(row["PII_Redacted"]),
                            int(row["Titles_Neutralized"]),
                            float(row["Trust_Score"]),
                            row["Compliance_Grade"],
                            processed_at
                        ))
            
            connect.commit()
            connect.close()
            return 'Success', current_session_id
    except Exception as e:
        return 'Error', str(e)
    
status, session_id = db_commit(summary_results)

output_df = pd.DataFrame([{
    'Vault_Status': status,
    'Session_ID': session_id,
    'Files_Archived': len(summary_results),
    'Timestamp': datetime.now().strftime("%d-%m-%Y %H:%M:%S")
}])

knio.output_tables[0] = knio.Table.from_pandas(output_df)