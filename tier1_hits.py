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
    }
]

# --- START --- TIER 1 --- START ---
def get_tier1(text):
    all_matches = []
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
                
    # Sort ascending and rule to let the longest win
    all_matches.sort( key=lambda m: (m["start"], -m["length"]))

    # collision resolver greedy
    result = []
    last_end = -1

    for m in all_matches:
        if m["start"] >= last_end:
            result.append(m)
            last_end = m["end"]

    return result
    
# --- END --- Tier1 masking layer ---

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
tier1_out = []

# Loop over all provided filepaths in dir
for content in input_df['Content']:
    tier1_matches = get_tier1(content)
    tier1_out.append(json.dumps(tier1_matches))

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_df['Filepath'],
    "Content": input_df['Content'],
    "Tier1_matches": tier1_out,
    }))