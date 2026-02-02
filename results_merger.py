import knime.scripting.io as knio
import pandas as pd
import json

# Set your preferred mode: "LABEL" or "STAR"
MASKING_MODE = "LABEL"

input_df = knio.input_tables[0].to_pandas()
pre_redacted = []

for index, row in input_df.iterrows():
    text = row['Content']
    
    # 1. Load hits from previous nodes
    # Using .get() with '[]' as fallback to prevent crashes if a node failed
    t1_hits = json.loads(row.get('Tier1_matches', '[]'))
    t2_hits = json.loads(row.get('Tier2_matches', '[]'))
    
    # 2. Combine all hits
    all_hits = t1_hits + t2_hits
    
    # 3. Resolve Collisions (Greedy approach again)
    # Sort by start (asc) and length (desc)
    all_hits.sort(key=lambda x: (x['start'], -x.get('length', 0)))
    
    final_mask_targets = []
    last_end = -1
    for hit in all_hits:
        if hit['start'] >= last_end:
            final_mask_targets.append(hit)
            last_end = hit['end']
    
    # 4. Apply Masking (Reverse Order)
    final_mask_targets.sort(key=lambda x: x['start'], reverse=True)
    
    masked_text = text
    for m in final_mask_targets:
        if MASKING_MODE == "LABEL":
            replacement = f"[{m['label']}]"
        else:
            # Preserve length if 'length' exists, else use span
            length = m.get('length', m['end'] - m['start'])
            replacement = "*" * length
            
        masked_text = masked_text[:m['start']] + replacement + masked_text[m['end']:]
    
    pre_redacted.append(masked_text)

# Prepare output for the LLM Node
output_df = input_df.copy()
output_df['Pre_redacted'] = pre_redacted

knio.output_tables[0] = knio.Table.from_pandas(output_df)