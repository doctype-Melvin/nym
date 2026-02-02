import knime.scripting.io as knio
import pandas as pd
import re

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
        mask = f'[{m["label"]}]'
        text = text[:m["start"]] + mask + text[m["end"]:]
    return text
    
# --- END --- Tier1 masking layer ---

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
tier1 = []

# Loop over all provided filepaths in dir
for content in input_df['Content']:
    current_content = content
    
    current_tier1_content = apply_tier1(current_content)
    tier1.append(current_tier1_content) # value for output table

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_df['Filepath'],
    "Content": input_df['Content'],
    "Tier1": tier1,
    }))