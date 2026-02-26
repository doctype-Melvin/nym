import knime.scripting.io as knio
import pandas as pd
import re
import json
import unicodedata
import hashlib
from collections import defaultdict

# Describe REGEX patterns
tier1_regex = [
    {
        "label": "E-MAIL",
        "pattern": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    },
    {
        "label": "TELEFON",
        "pattern": r"(?:(?:\+?49[ \-\.\(\)]?)?(?:(?:\(?0\d{1,5}\)?)|(?:\d{1,5}))[ \-\.\(\)]?(?:\d[ \-\.\(\)]?){5,10}\d)"
    },
    {
        "label": "WEB_LINK",
        "pattern": r"\b(?<!mailto:)(?<!@)(?:https?:\/\/)?(?:www\.)?(?!\d)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:\/[^\s<>\"'@]*|(?!\S))?\b(?![\w@./])"
    },
    {
        "label": "SOCIAL_MEDIA",
        "pattern": r"@[A-Za-z0-9](?:[A-Za-z0-9._-]{1,28}[A-Za-z0-9])?"
    },
    {
        "label": "STADT",
        "pattern": r"\b\d{5}\b"
    },
    {
        "label": "DATUM",
        "pattern": r"\b\d{1,2}\.\d{1,2}\.(\d{4}|\d{2})\b"
    },
    {
        "label": "DATUM",
        "pattern": r"(?i)\b\d{1,2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s\d{4}\b"
    },
    {
        "label": "DATUM",
        "pattern": r"(?i)\b\d{2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s\d{4}\b"
    },
    {
        "label": "DATUM",
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
    markdown = text
    new_logs = []
    occ_counter = defaultdict(int)

    # for each rule in list
    for rule in tier1_regex:
#        matches = set(re.findall(rule['pattern'], text, flags=re.IGNORECASE)) # using set to avoid dupes
        label = rule['label']
        pattern = rule['pattern']

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            match_text = match.group()
            text_hash = make_pii_hash(match_text)
            occ_counter[match_text] += 1
            current_idx = occ_counter[match_text]

            # write log entries
            new_logs.append({
                'file': filename,
                "pii_hash": text_hash,
                'label': label,
                'occurrence_index': current_idx
            })

            # perform redaction
            redaction_label = f"[{label}]"
            #text = re.sub(rf'\b{re.escape(match)}\b', redaction_label, text)
            text = text.replace(match_text, redaction_label)

    return new_logs, text, markdown

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
original_in = []
normalized_contents = []
markdown_pass = []

try: 
    cumulative_log = knio.input_tables[1].to_pandas().to_dict('records')
except:
    cumulative_log = []

# Loop over all provided filepaths in dir
for content, filepath in zip(input_df['Content'], input_df['Filepath']):
    
    new_logs, clean_text, markdown = get_tier1(content, filepath)

    normalized_contents.append(clean_text)
    original_in.append(content)
    markdown_pass.append(markdown)


    for log in new_logs:
        cumulative_log.append({
            'filepath': filepath,
            'pii_hash': log['pii_hash'],
            'label': log['label'],
            'occurrence_index': log['occurrence_index'],
            'confidence_score': 1.0,
            'event_code': 'T1-RGX',
            'status': 'REDACT',
            'is_manual': 0
        })
    
knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_df['Filepath'],
    "Original": original_in,
    "Markdown": markdown_pass,
    "Output": normalized_contents
    }))

knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(cumulative_log))