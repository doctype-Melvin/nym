import sqlite3
import pandas as pd
import knime.scripting.io as knio
import uuid
import hashlib

# cumulative_log dataframe
log_df = knio.input_tables[0].to_pandas()
db_path = "complyable_vault.db"

def archive_audit_trail(df):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    records_added = 0
    for _, row in df.iterrows():
        rec_uuid = str(uuid.uuid4())

        # Integrity has based on SHA-256 fingerprint of event
        # Proof that record wasn't modified
        hash_string = f'{row["Timestamp"]}{row["Filepath"]}{row["Description"]}'
        integrity_hash = hashlib.sha256(hash_string.encode()).hexdigest()

        cursor.execute('''
            INSERT INTO audit_trail (
                       record_uuid,
                       filepath,
                       event_code,
                       event_type,
                       description,
                       confidence_score,
                       details,
                       integrity_hash
                       )
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       ''', (
                           rec_uuid,
                           row['Filepath'],
                           row.get('Event_Code', 'GEN-01'),
                           row['Event_tyle'],
                           row['Description'],
                           float(row['Confidence_Score']),
                           row['Details'],
                           integrity_hash
                       ))
        records_added += 1

    connect.commit()
    connect.close()
    return records_added

total_saved = archive_audit_trail(log_df)

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({"Records_Archived": total_saved}))