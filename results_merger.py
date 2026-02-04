import knime.scripting.io as knio
import pandas as pd
import json

def merge_and_log(t1_list, t2_list, filepath):

    t1_list = t1_list if isinstance(t1_list, list) else []
    t2_list = t2_list if isinstance(t2_list, list) else []

    all_matches = []
    new_logs = []

    for match in t1_list: match['source'] = 'Tier 1'
    for match in t2_list: match['source'] = 'Tier 2'

    merged = t1_list + t2_list
    merged.sort(key=lambda x: (x['start'], -x.get('length', (x['end']-x['start']))))
    
    last_end = -1

    for match in merged:
        if match['start'] < last_end:
            new_logs.append({
                'Timestamp': pd.Timestamp.now().strftime('%D.%m.%Y %H:%M:%S'),
                'Filepath': filepath,
                'Event_Type': 'Conflict_Resolution',
                'Description': f"Removed overlapping {match['label']} at index {match['start']}",
                'Confidence_Score': 1.0,
                'Details': f"Conflict at index {match['start']}-{match['end']}",
            })
            continue
        
        all_matches.append(match)
        last_end = match['end']

    return all_matches, new_logs

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()

pre_redacted = []

try:
    cumulative_log = knio.input_tables[1].to_pandas().to_dict('records')
except:
    cumulative_log = []

for tier1_list, tier2_list, filepath in zip(input_df['Tier1_matches'], input_df['Tier2_matches'], input_df['Filepath']):

    result, new_logs = merge_and_log(tier1_list, tier2_list, filepath)

    for log in new_logs:
        cumulative_log.append({
            'Timestamp': pd.Timestamp.now().strftime('%D.%m.%Y %H:%M:%S'),
            'Filepath': filepath,
            'Event_Type': 'Conflict_Resolution',
            'Description': f"Removed overlapping {log['label']} at index {log['start']}",
            'Confidence_Score': 1.0,
            'Details': 'Overlapping match discarded',
            'Start': log['start'],
            'End': log['end']
        })

for index, row in input_df.iterrows():
    text = row['Content']
    filepath = row['Filepath']

    # 1. Load hits from previous nodes
    # Using .get() with '[]' as fallback to prevent crashes if a node failed
    raw_t1 = row.get('Tier1_matches', '[]')  
    raw_t2 = row.get('Tier2_matches', '[]')
    
    # Ensure we are dealing with strings before loading
    t1_list = json.loads(raw_t1) if isinstance(raw_t1, str) else []
    t2_list = json.loads(raw_t2) if isinstance(raw_t2, str) else []

    result, conflicts = merge_and_log(t1_list, t2_list, filepath)
    cumulative_log.extend(conflicts)
        
    # 2. Resolve Collisions (Greedy approach again)
    # Sort by start (asc) and length (desc)
    result.sort(key=lambda x: x['start'], reverse=True)
    masked_text = text
    
    for match in result:#
        replacement = f"[{match['label']}]"
        masked_text = masked_text[:match['start']] + replacement + masked_text[match['end']:]

    pre_redacted.append(masked_text)

output_df = input_df.copy()
output_df['Redacted'] = pre_redacted
knio.output_tables[0] = knio.Table.from_pandas(output_df)

knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(cumulative_log))