import hashlib
import sqlite3
import knime.scripting.io as knio

def generate_integrity_hash(text):
    return hashlib.sha256(text.encode('utf-8').hexdigest())

data = knio.input_tables[0].to_pandas()
connect = sqlite3.connect("complyable_vault.db")
cursot = connect.cursor()

for _, row in data.iterrows():
    