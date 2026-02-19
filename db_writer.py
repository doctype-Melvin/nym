import hashlib
import sqlite3
import knime.scripting.io as knio

def generate_integrity_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
db_path="../complyable_app/data/vault/complyable_vault.db"
data = knio.input_tables[0].to_pandas()
connect = sqlite3.connect(db_path)
cursor = connect.cursor()

for _, row in data.iterrows():
    i_hash = generate_integrity_hash(str(row['Output_final']))

    cursor.execute("""
        INSERT OR REPLACE INTO pending_review 
        (filepath, content, output_final, status, integrity_hash)
        VALUES (?, ?, ?, ?, ?)
    """, (row['Filepath'], row['Content'], row['Output_final'], 'PENDING', i_hash))
    
connect.commit()
connect.close()

knio.output_tables[0] = knio.Table.from_pandas(data)