import hashlib
import sqlite3
import knime.scripting.io as knio

def generate_integrity_hash(text):
    return hashlib.sha256(text.encode('utf-8').hexdigest())

data = knio.input_tables[0].to_pandas()
connect = sqlite3.connect("complyable_vault.db")
cursor = connect.cursor()

for _, row in data.iterrows():
    i_hash = generate_integrity_hash(row['Content'])

    cursor.execute("""
                   INSERT OR REPLACE INTO pending_review
                   (filepath, content, text, layout_conf_score, status, integrity_hash)
                   VALUES (?, ?, ?, ?, ?, ?)
                   """, (row['Filepath'], row['Content'], row['Text'], row['layout_conf_score'], 'PENDING', i_hash))
    
connect.commit()
connect.close()