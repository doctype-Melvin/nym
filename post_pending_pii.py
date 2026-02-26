import sqlite3
import pandas as pd
import knime.scripting.io as knio
import os
from dotenv import load_dotenv

load_dotenv('./')
db_path = os.getenv('DB_PATH', "../complyable_app/data/vault/complyable_vault.db")

# This is the cumulative_log from your Tiers
log_df = knio.input_tables[0].to_pandas()

def stage_pending_pii(df):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    target_files = tuple(df['filepath'].unique())
    if len(target_files) == 1:
        cursor.execute("DELETE FROM pending_pii WHERE filepath = ?", (target_files[0],))
    else:
        cursor.execute(f"DELETE FROM pending_pii WHERE filepath IN {target_files}")

    records_added = 0
    for _, row in df.iterrows():
        # Clean landing into the staging table
        cursor.execute('''
            INSERT INTO pending_pii (
                       filepath,
                       pii_text,
                       pii_hash,
                       label,
                       occurrence_index,
                       confidence_score,
                       event_code,
                       status,
                       is_manual
                       )
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'REDACT', 0)
                       ''', (
                           str(row['filepath']),
                           str(row['pii_text']),
                           str(row.get('pii_hash', '')),
                           str(row.get('label', 'UNKNOWN')),
                           row.get('occurrence_index', 1),
                           float(row.get('confidence_score', 0.0)),
                           str(row.get('event_code', 'T1-RGX'))
                       ))
        records_added += 1

    connect.commit()
    connect.close()
    return records_added

# Check if log_df is empty to avoid errors
if not log_df.empty:
    total_staged = stage_pending_pii(log_df)
else:
    total_staged = 0

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame([{"Records_Staged": total_staged}]))