import knime.scripting.io as knio
import pandas as pd
import re
import sqlite3

db_path = "complyable_vault.db"
connect = sqlite3.connect(db_path)

job_table = pd.read_sql_query("SELECT original, neutral FROM job_dict", connect)
connect.close()

redacted_table = knio.input_tables[0].to_pandas()

try: 
    cumulative_log = knio.input_tables[1].to_pandas().to_dict('records')
except:
    cumulative_log = []

# Sort by length descending to prevent substring collisions
job_table = job_table.iloc[job_table['original'].str.len().argsort()[::-1]].reset_index(drop=True)

def neutralizer(text, filepath):
    events = []
    current = str(text)
    
    # Standard Date Format to match Tier 1/2
    ts_format = '%d.%m.%Y %H:%M:%S'
    
    kauf_patterns = [
        (r"\b(\w+)(kaufmann|kauffrau)\b", r"\1fachkraft", "Group Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s+für\b", "Fachkraft für", "Title Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s\b", "Fachkraft ", "Title Neutralization")
    ]

    for pattern, replacement, label in kauf_patterns:
        found = re.findall(pattern, current, flags=re.IGNORECASE)
        if found:
            for match in found:
                match_text = "".join(match) if isinstance(match, tuple) else match
                events.append({
                    'Timestamp': pd.Timestamp.now().strftime(ts_format),
                    'Filepath': filepath,
                    'Event_type': 'Neutralization',
                    'Description': f"Pattern: '{match_text}' -> '{replacement}'",
                    'Start': 0, # Global context
                    'End': len(current),
                    'Confidence_Score': 1.0, # Rule-based
                    'Details': f"Regex-Rule: {label}"
                })
            current = re.sub(pattern, replacement, current, flags=re.IGNORECASE)

    for _, row in job_table.iterrows():
        target = rf'\b{re.escape(str(row["original"]))}\b'
        if re.search(target, current, flags=re.IGNORECASE):
            events.append({
                'Timestamp': pd.Timestamp.now().strftime(ts_format),
                'Filepath': filepath,
                'Event_type': 'Neutralization',
                'Description': f"Dict: '{row['original']}' -> '{row['neutral']}'",
                'Start': 0,
                'End': len(current),
                'Confidence_Score': 0.9, # Matches entry in (incomplete) lookup
                'Details': 'Manual Dictionary Match' 
            })
            current = re.sub(target, row["neutral"], current, flags=re.IGNORECASE)
        
    if not events: # handle no-matching
        events.append({
            'Timestamp': pd.Timestamp.now().strftime(ts_format),
            'Filepath': filepath,
            'Event_type': 'Neutralization',
            'Description': 'No gender-specific phrases detected.',
            'Start': 0,
            'End': 0,
            'Confidence_Score': 0.85, # 100% sure nothing matched based on (incomplete) lookup
            'Details': 'Process complete: No changes required'
        })
    
    return current, events

# Main Processing
neutralized_output = []
for index, row in redacted_table.iterrows():
    neu_text, new_logs = neutralizer(row['Redacted'], row['Filepath'])
    neutralized_output.append(neu_text)
    cumulative_log.extend(new_logs)

output_df = redacted_table.copy()
output_df["Output_final"] = neutralized_output 

knio.output_tables[0] = knio.Table.from_pandas(output_df)
knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(cumulative_log))