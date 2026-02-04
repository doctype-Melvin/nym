import knime.scripting.io as knio
import pandas as pd
import re
import json

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

# --- START --- TIER 1 --- START ---
def get_tier1(text, filename):
    all_matches = []
    new_logs = []
    # for each rule in list
    for rule in tier1_regex:
        # find matches for the current pattern
        for match in re.finditer(rule["pattern"], text):
            # print(match.start(), match.end(), rule["label"])
            all_matches.append({
                "start": match.start(),
                "end": match.end(), 
                "label": rule["label"],
                "length": match.end() - match.start()
                })
            new_logs.append({
                'File': filename,
                'Node': 'Tier 1 Regex',
                'Action': 'Redact',
                'Detail': f"found: {rule['label']}",
                "start": match.start(),
                "end": match.end(), 
            })
                
    # Sort ascending and rule to let the longest win
    all_matches.sort( key=lambda m: (m["start"], -m["length"]))

    # collision resolver greedy
    result = []
    last_end = -1

    for m in all_matches:
        if m["start"] >= last_end:
            result.append(m)
            last_end = m["end"]

    return result, new_logs
    
# --- END --- Tier1 masking layer ---

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
tier1_out = []

try: 
    cumulative_log = knio.input_tables[1].to_pandas().to_dict('records')
except:
    cumulative_log = []

#tier1_results = []

# Loop over all provided filepaths in dir
for content, filepath in zip(input_df['Content'], input_df['Filepath']):
    
    matches, new_logs = get_tier1(content, filepath)

 #   tier1_results.append(json.dumps(matches))

    for log in new_logs:
        cumulative_log.append({
            'Timestamp': pd.Timestamp.now().strftime('%D.%m.%Y %H:%M:%S'),
            'Filepath': filepath,
            'Event_type': 'PII_Detection_T1',
            'Description': log['Detail'],
            'Start': log['start'],
            'End': log['end'],
            'Confidence_Score': 1.0,
            'Details': "Regex Pattern Match"
        })
    
    tier1_out.append(json.dumps(matches))

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_df['Filepath'],
    "Content": input_df['Content'],
    "Tier1_matches": tier1_out,
    }))

knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(cumulative_log))