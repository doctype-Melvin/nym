import knime.scripting.io as knio
import pandas as pd
import spacy
import re
import json

nlp = spacy.load("de_core_news_lg")

ent_labels = ["PER", "LOC", 'PHONE', 'EMAIL']

# Remove all unnecessary whitespace and linebreaks from text
clean_text = lambda t:  ' '.join(t.replace('\n', ' ').split())

# --- START --- TIER 2 --- START ---
def get_tier2(doc):
    matches = []
    match_log = []
    # for each rule in list
    for ent in doc.ents:
        if ent.label_ in ent_labels:
            # print(match.start(), match.end(), rule["label"])
            matches.append({
                "start": ent.start_char,
                "end": ent.end_char, 
                "label": ent.label_,
                "length": ent.end_char - ent.start_char
                })
            match_log.append(f'{clean_text(ent.text)} ({ent.label_})')

    return [matches, match_log]

# --- END --- Tier1 masking layer ---

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()

all_matches = []
all_logs = []
# Loop over all provided filepaths in dir
for index, row in input_df.iterrows():
    
    content = row['Content']

    doc = nlp(content)

    matches = get_tier2(doc)

    all_matches.append(json.dumps(matches[0]))
    all_logs.append(json.dumps(matches[1]))

output_df = input_df.copy()
output_df['Tier2_matches'] = all_matches
output_df['Tier2_logs'] = all_logs

knio.output_tables[0] = knio.Table.from_pandas(output_df)