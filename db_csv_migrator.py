import sqlite3
import pandas as pd
import knime.scripting.io as knio
from datetime import datetime

# 1. Get the enriched dictionary from the KNIME input port
new_data = knio.input_tables[0].to_pandas()

# Ensure column names match our DB schema
# Expected columns: ['Original', 'Neutral', 'Category']
db_path = "complyable_vault.db"

def migrate_to_vault(df):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 2. Use 'INSERT OR REPLACE' to handle updates to existing terms
        # We add the current timestamp to the 'last_updated' column
        current_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO job_dict (original, neutral, category, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (str(row['Original']), str(row['Neutral']), str(row['Category']), current_ts))
        
        conn.commit()
        count = len(df)
        conn.close()
        return "Success", f"Migrated {count} titles to the Vault."
    except Exception as e:
        return "Error", str(e)

# Execute
status, message = migrate_to_vault(new_data)

# 3. Output for KNIME
output_df = pd.DataFrame([{"Status": status, "Details": message}])
knio.output_tables[0] = knio.Table.from_pandas(output_df)