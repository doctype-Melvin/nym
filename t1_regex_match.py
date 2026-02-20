import knime.scripting.io as knio
import pandas as pd
import re
import json
import unicodedata
import hashlib

# Describe REGEX patterns

tier1_regex = [
    {
        "label": "EMAIL",
        "pattern": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    },
    {
        "label": "PHONE_DE",
        "pattern": r"(?:(?:\+?49[ \-\.\(\)]?)?(?:(?:\(?0\d{1,5}\)?)|(?:\d{1,5}))[ \-\.\(\)]?(?:\d[ \-\.\(\)]?){5,10}\d)"
    },
    {
        "label": "WEB",
        "pattern": r"\b(?<!mailto:)(?<!@)(?:https?:\/\/)?(?:www\.)?(?!\d)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:\/[^\s<>\"'@]*|(?!\S))?\b(?![\w@./])"
    },
    {
        "label": "SOCI",
        "pattern": r"@[A-Za-z0-9](?:[A-Za-z0-9._-]{1,28}[A-Za-z0-9])?"
    },
    {
        "label": "LOC",
        "pattern": r"\b\d{5}\b"
    },
    {
        "label": "DATE",
        "pattern": r"\b\d{1,2}\.\d{1,2}\.(\d{4}|\d{2})\b"
    },
    {
        "label": "DATE",
        "pattern": r"(?i)\b\d{1,2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s\d{4}\b"
    },
    {
        "label": "DATE",
        "pattern": r"(?i)\b\d{2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s\d{4}\b"
    },
    {
        "label": "DATE",
        "pattern": r"(?i)\b\d{1,2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s'\d{2}\b"
    }
]

# Standardize hashing function
def make_pii_hash(text):
    clean_text = unicodedata.normalize('NFC', str(text)).strip()
    return hashlib.sha256(clean_text.encode('utf-8')).hexdigest()

# Title casing function
def to_titlecase(text):
    text = re.sub(r'\b([A-ZÜÖÄ])(?:\s([A-ZÜÖÄ]))+\b', 
                  lambda m: m.group(0).replace(" ", ""), text)
    def replace_match(match):
        word = match.group(0)
        return word.lower().title() if len(word) >= 3 else word
    return re.sub(r'\b[A-ZÜÖÄß]{3,}\b', replace_match, text)

# --- TIER 1 REGEX matching & redacting logic ---
def get_tier1(text, filename):
    text = to_titlecase(unicodedata.normalize('NFC', text))
    all_matches = []
    new_logs = []

    # for each rule in list
    for rule in tier1_regex:
        matches = set(re.findall(rule['pattern'], text)) # using set to avoid dupes
        
        for match in matches:
            text_hash = make_pii_hash(match)
            label = rule['label']

            # write log entries
            all_matches.append({ # this might be redundant
                "hash": text_hash,
                "label": rule["label"]
                })
            new_logs.append({
                'File': filename,
                'Node': 'Tier 1 Regex',
                'Action': 'Redact',
                "PII_hash": text_hash,
                'Label': label
            })

            # perform redaction
            redaction_label = f"[{label}]"
            text = re.sub(rf'\b{re.escape(match)}\b', redaction_label, text)

    return all_matches, new_logs, text

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
tier1_out = [] # this might be redundant - no need to pass the list of matches
normalized_contents = []

try: 
    cumulative_log = knio.input_tables[1].to_pandas().to_dict('records')
except:
    cumulative_log = []

# Loop over all provided filepaths in dir
for content, filepath in zip(input_df['Content'], input_df['Filepath']):
    
    matches, new_logs, clean_text = get_tier1(content, filepath)

    normalized_contents.append(clean_text)


    for log in new_logs:
        cumulative_log.append({
            'Timestamp': pd.Timestamp.now().strftime('%d.%m.%Y %H:%M:%S'),
            'Filepath': filepath,
            'Event_type': 'PII_hashed',
            'PII_hash': log['PII_hash'],
            'Description': f"Hashed {log['Label']}",
            'Confidence_score': 1.0,
            'Details': "Tier1 Regex Pattern Match"
        })
    
    tier1_out.append(json.dumps(matches))

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_df['Filepath'],
    "Content": normalized_contents,
    "Tier1_matches": tier1_out,
    }))

knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(cumulative_log))