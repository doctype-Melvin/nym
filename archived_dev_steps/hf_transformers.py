import knime.scripting.io as knio
import pandas as pd
from transformers import pipeline
import json

# 1. Initialize the Pipeline (This will download the model on the first run)
# We use 'aggregation_strategy="simple"' to merge multi-token entities (like "Dorf-straße")
ner_pipeline = pipeline(
    "ner", 
    model="distilbert/distilbert-base-german-cased", 
    aggregation_strategy="simple"
)

input_df = knio.input_tables[0].to_pandas()
hf_hits_col = []

for index, row in input_df.iterrows():
    text = row['Content']
    
    # 2. Run the Transformer
    results = ner_pipeline(text)
    
    current_hits = []
    for entity in results:
        # The model uses labels like 'LOC', 'PER', 'ORG'
        current_hits.append({
            "start": int(entity['start']),
            "end": int(entity['end']),
            "label": entity['entity_group'],
            "text": entity['word'],
            "length": (int(entity['end'] - int(entity['start']))),
           # "score": float(entity['score']) # Confidence score
        })
    
    hf_hits_col.append(json.dumps(current_hits))

# 3. Add to our modular table
output_df = input_df.copy()
output_df["HF_matches"] = hf_hits_col

knio.output_tables[0] = knio.Table.from_pandas(output_df)
