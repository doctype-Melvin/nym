import sqlite3
import pandas as pd
import knime.scripting.io as knio
import uuid
import hashlib

# cumulative_log dataframe
log_df = knio.input_tables[0].to_pandas()
db_path="../complyable_app/data/vault/complyable_vault.db"

def archive_audit_trail(df):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    records_added = 0
    for _, row in df.iterrows():
        rec_uuid = str(uuid.uuid4())

        # Integrity has based on SHA-256 fingerprint of event
        # Proof that record wasn't modified
        hash_string = f'{row["Timestamp"]}{row["Filepath"]}{row.get("PII_Hash", "")}{row["Description"]}'
        integrity_hash = hashlib.sha256(hash_string.encode()).hexdigest()

        cursor.execute('''
            INSERT INTO audit_trail (
                       record_uuid,
                       filepath,
                       event_type,
                       description,
                       pii_hash,
                       confidence_score,
                       integrity_hash
                       )
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ''', (
                           str(rec_uuid),
                           str(row['Filepath']),
                           str(row['Event_type']),
                           str(row['Description']),
                           str(row.get('PII_Hash', '')),
                           float(row.get('Confidence_Score', 0.0)),
                           integrity_hash
                       ))
        records_added += 1

    connect.commit()
    connect.close()
    return records_added

total_saved = archive_audit_trail(log_df)

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame([{"Records_Archived": total_saved}]))