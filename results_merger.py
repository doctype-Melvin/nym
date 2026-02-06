import knime.scripting.io as knio
import pandas as pd
import json

def merge_and_resolve(t1_list, t2_list, filepath):
    t1_list = t1_list if isinstance(t1_list, list) else []
    t2_list = t2_list if isinstance(t2_list, list) else []

    for match in t1_list: match['source'] = 'Tier 1'
    for match in t2_list: match['source'] = 'Tier 2'

    merged = t1_list + t2_list
    # Sort by start position, then by length (descending) to let longer matches win
    merged.sort(key=lambda x: (x['start'], -x.get('length', (x['end']-x['start']))))
    
    final_matches = []
    conflict_logs = []
    last_end = -1

    for match in merged:
        if match['start'] < last_end:
            # This is a conflict. We log it but don't add to final_matches
            conflict_logs.append({
                'Timestamp': pd.Timestamp.now().strftime('%d.%m.%Y %H:%M:%S'),
                'Filepath': filepath,
                'Event_type': 'Conflict_Resolution',
                'Description': f"Removed overlapping {match['label']} from {match['source']}",
                'Start': match['start'],
                'End': match['end'],
                'Confidence_Score': 1.0,
                'Details': f"Conflict: Overlapped by previous match ending at {last_end}"
            })
            continue
        
        final_matches.append(match)
        last_end = match['end']

    return final_matches, conflict_logs

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
pre_redacted = []

try:
    cumulative_log = knio.input_tables[1].to_pandas().to_dict('records')
except:
    cumulative_log = []

for index, row in input_df.iterrows():
    text = row['Content']
    filepath = row['Filepath']

    # 1. Load hits safely
    raw_t1 = row.get('Tier1_matches', '[]')  
    raw_t2 = row.get('Tier2_matches', '[]')
    t1_list = json.loads(raw_t1) if isinstance(raw_t1, str) else []
    t2_list = json.loads(raw_t2) if isinstance(raw_t2, str) else []

    # 2. Merge and identify conflicts
    final_hits, conflicts = merge_and_resolve(t1_list, t2_list, filepath)
    
    # 3. Add conflicts to our master audit trail
    cumulative_log.extend(conflicts)
        
    # 4. Apply redactions (Back-to-Front to preserve indices)
    final_hits.sort(key=lambda x: x['start'], reverse=True)
    masked_text = text
    for match in final_hits:
        replacement = f"[{match['label']}]"
        masked_text = masked_text[:match['start']] + replacement + masked_text[match['end']:]

    pre_redacted.append(masked_text)

output_df = input_df.copy()
output_df['Redacted_Content'] = pre_redacted # Unified name for next node

knio.output_tables[0] = knio.Table.from_pandas(output_df)
knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(cumulative_log))