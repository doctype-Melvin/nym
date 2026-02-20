import knime.scripting.io as knio
import pandas as pd
import spacy
import re
import sqlite3
import unicodedata
import hashlib
from datetime import datetime

# --- CONFIG ---
nlp = spacy.load("de_core_news_lg")

def make_pii_hash(text):
    clean_text = unicodedata.normalize('NFC', str(text)).strip()
    return hashlib.sha256(clean_text.encode('utf-8')).hexdigest()

def is_person_related(token):
    text = token.text.lower()
    blacklist = {"september", "oktober", "november", "dezember"}
    if text in blacklist or token.ent_type_ in ["DATE", "TIME", "CARDINAL"]: return False
    person_suffixes = ("er", "in", "ent", "ant", "ist", "kraft", "experte", "leiter")
    return text.endswith(person_suffixes) or token.ent_type_ == "PER"

# --- DB DATA ---
db_path = "../complyable_app/data/vault/complyable_vault.db" 
conn = sqlite3.connect(db_path)
job_table = pd.read_sql_query("SELECT original, neutral FROM job_dict", conn)
conn.close()
job_table = job_table.iloc[job_table['original'].str.len().argsort()[::-1]].reset_index(drop=True)

# --- INPUTS ---
input_df = knio.input_tables[0].to_pandas()
try:
    cumulative_log = knio.input_tables[1].to_pandas().to_dict('records')
except:
    cumulative_log = []

# --- CORE LOGIC ---
final_texts = []
ts_format = '%d.%m.%Y %H:%M:%S'

for index, row in input_df.iterrows():
    current = str(row['Content'])
    filepath = row['Filepath']
    
    # 1. Patterns (Your v1 logic)
    kauf_patterns = [
        (r"\b(\w+)(kaufmann|kauffrau)\b", r"\1fachkraft", "Group Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s+für\b", "Fachkraft für", "Title Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s\b", "Fachkraft ", "Title Neutralization")
    ]
    for pattern, replacement, label in kauf_patterns:
        for match in re.finditer(pattern, current, flags=re.IGNORECASE):
            match_text = match.group()
            text_hash = make_pii_hash(match_text)
            cumulative_log.append({
                'timestamp': datetime.now().strftime(ts_format),
                'filepath': filepath,
                'event_code': 'T3-GIP', # Gender-Identifying-Phrase Neutralized Regex
                'pii_hash': text_hash,
                'confidence_score': 1.0
            })
        current = re.sub(pattern, replacement, current, flags=re.IGNORECASE)

    # 2. Dictionary (Your v1 logic)
    for _, d_row in job_table.iterrows():
        original = str(d_row['original'])
        target = rf'\b{re.escape(str(original))}\b'
        match = re.search(target, current, flags=re.IGNORECASE)
        if match:
            actual_text = match.group()
            text_hash = make_pii_hash(actual_text)
            cumulative_log.append({
                'timestamp': datetime.now().strftime(ts_format),
                'filepath': filepath,
                'event_code': 'T3-GIP', # Gender-Identifying-Phrase Neutralized Dictionary
                'pii_hash': text_hash,
                'confidence_score': 0.9
            })
            current = re.sub(target, d_row["neutral"], current, flags=re.IGNORECASE)

    # 3. Sensor (Linguistic Flagging for what wasn't caught above)
    doc = nlp(current)
    for token in doc:
        if (token.pos_ in ["NOUN", "PROPN", "PRON"]) and (is_person_related(token) or token.pos_ == "PRON"):
            morph = token.morph.to_dict()
            if "Gender" in morph:
                text_hash = make_pii_hash(token.text)
            cumulative_log.append({
                    'timestamp': datetime.now().strftime(ts_format),
                    'filepath': filepath,
                    'event_code': 'T3-FLG', # Gender Flag (not neutralized)
                    'pii_hash': text_hash,
                    'Confidence_Score': 0.75
                })
    
    final_texts.append(current)

# --- OUTPUT ---
output_df = input_df.copy()
output_df["Output_final"] = final_texts
knio.output_tables[0] = knio.Table.from_pandas(output_df)
knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(cumulative_log))