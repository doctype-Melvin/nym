import knime.scripting.io as knio
import pandas as pd
import spacy
import re
import sqlite3
from datetime import datetime

# --- CONFIG ---
nlp = spacy.load("de_core_news_lg")

def is_person_related(token):
    text = token.text.lower()
    blacklist = {"september", "oktober", "november", "dezember", "zimmer", "nummer", "uhr"}
    if text in blacklist or token.ent_type_ in ["DATE", "TIME", "CARDINAL"]: return False
    person_suffixes = ("er", "in", "ent", "ant", "ist", "kraft", "experte", "leiter")
    return text.endswith(person_suffixes) or token.ent_type_ == "PER"

# --- DB DATA ---
db_path = "complyable_vault.db" # Ensure path is correct for your env
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
    current = str(row['Redacted'])
    filepath = row['Filepath']
    
    # 1. Patterns (Your v1 logic)
    kauf_patterns = [
        (r"\b(\w+)(kaufmann|kauffrau)\b", r"\1fachkraft", "Group Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s+für\b", "Fachkraft für", "Title Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s\b", "Fachkraft ", "Title Neutralization")
    ]
    for pattern, replacement, label in kauf_patterns:
        found = re.findall(pattern, current, flags=re.IGNORECASE)
        if found:
            for match in found:
                match_text = "".join(match) if isinstance(match, tuple) else match
                cumulative_log.append({
                    'Timestamp': datetime.now().strftime(ts_format),
                    'Filepath': filepath, 'Event_type': 'Neutralization',
                    'Description': f"Pattern: '{match_text}' -> '{replacement}'",
                    'Start': 0, 'End': len(current), 'Confidence_Score': 1.0, 'Details': f"Regex-Rule: {label}"
                })
            current = re.sub(pattern, replacement, current, flags=re.IGNORECASE)

    # 2. Dictionary (Your v1 logic)
    for _, d_row in job_table.iterrows():
        target = rf'\b{re.escape(str(d_row["original"]))}\b'
        if re.search(target, current, flags=re.IGNORECASE):
            cumulative_log.append({
                'Timestamp': datetime.now().strftime(ts_format),
                'Filepath': filepath, 'Event_type': 'Neutralization',
                'Description': f"Dict: '{d_row['original']}' -> '{d_row['neutral']}'",
                'Start': 0, 'End': len(current), 'Confidence_Score': 0.9, 'Details': 'Manual Dictionary Match'
            })
            current = re.sub(target, d_row["neutral"], current, flags=re.IGNORECASE)

    # 3. Sensor (Linguistic Flagging for what wasn't caught above)
    doc = nlp(current)
    for token in doc:
        if (token.pos_ in ["NOUN", "PROPN", "PRON"]) and (is_person_related(token) or token.pos_ == "PRON"):
            morph = token.morph.to_dict()
            if "Gender" in morph:
                # We log this as a flag because it wasn't replaced by patterns/dict
                cumulative_log.append({
                    'Timestamp': datetime.now().strftime(ts_format),
                    'Filepath': filepath, 'Event_type': 'Compliance_Flag',
                    'Description': f"Gendered term '{token.text}' detected",
                    'Start': token.idx, 'End': token.idx + len(token.text),
                    'Confidence_Score': 0.75, 'Details': "Morphology hit: Flagged for review"
                })
    
    final_texts.append(current)

# --- OUTPUT ---
output_df = input_df.copy()
output_df["Output_final"] = final_texts
knio.output_tables[0] = knio.Table.from_pandas(output_df)
knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(cumulative_log))