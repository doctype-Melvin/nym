MASKING_MODE = "LABEL"

import knime.scripting.io as knio
import pandas as pd
import re

# Describe REGEX patterns
patterns = [
    {"label": "EMAIL",
    "pattern": [{"TEXT": {"REGEX": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"}}]},
    {"label": "PHON1",
    "pattern": [{"TEXT": {"REGEX": r"(?:\+49|0049|0)(?:\s?\d{2,5})(?:\s?\d{4,10})"}}]},
    {"label": "PHON2",
    "pattern": [{"TEXT": {"REGEX": r"(?:\+49|0)[-/\s.]?\d{2,5}[-/\s.]?\d{4,10}"}}]},
    {"label": "PHON3",
    "pattern": [{"TEXT": {"REGEX": r"(?:\+49|0)\s?\(0\)\s?\d{2,5}\s?\d{4,10}"}}]},
    {"label": "SOCI",
    "pattern": [{"TEXT": {"REGEX": r"@[a-zA-Z0-9_]{2,30}(?=$| )"}}]},
    {"label": "WEB",
    "pattern": [{"TEXT": {"REGEX": r"\b(?<!mailto:)(?<!@)(?:https?:\/\/)?(?:www\.)?(?!\d)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:\/[^\s<>\"'@]*|(?!\S))?\b(?![\w@./])"}}]},
]


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
    }

]

ent_labels = ["PER", "LOC", 'PHONE', 'EMAIL']

# --- START --- TIER 1 masking layer --- START ---
def apply_tier1(text):
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

    # Sort reverse to prevent character offset while cutting
    result.sort( key=lambda m: m["start"], reverse=True)

    # mask matches in text
    # actual redaction
    for m in result:
        if MASKING_MODE == "LABEL":
            mask = f'[{m["label"]}]'
        else: 
            mask = '*' * m['length']
        text = text[:m["start"]] + mask + text[m["end"]:]
        #print(text)
    return text
    
# --- END --- Tier1 masking layer ---

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
tier1 = []

# Loop over all provided filepaths in dir
for path in input_df['Filepath']:
    current_content = input_df['Content']
    
    tier1.append(apply_tier1(current_content)) # value for output table

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_df['Filepath'],
    "Content": current_content,
    "Tier1": tier1,
    }))