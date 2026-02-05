import knime.scripting.io as knio
import pandas as pd
import re

job_table = knio.input_tables[0].to_pandas()
pre_redacted_table = knio.input_tables[1].to_pandas()

try: 
    cumulative_log = knio.input_tables[2].to_pandas().to_dict('records')
except:
    cumulative_log = []


sort_idx = job_table['Original'].str.len().argsort()[::-1] # sort by integer position //[::-1] = descending 
job_table = job_table.iloc[sort_idx].reset_index(drop=True) # iloc by integer position 

def neutralizer(text, filepath):
    events = []
    current = str(text)
    
    kauf_patterns = [
        (r"\b(\w+)(kaufmann|kauffrau)\b", r"\1kaufleute", "Group Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s+für\b", "Fachkraft für", "Title Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s\b", "Fachkraft ", "Title Neutralization")
    ]

    for pattern, replacement, label in kauf_patterns:
        found = re.findall(pattern, current, flags=re.IGNORECASE)
        if found:
            for match in found:
                match_text = "".join(match) if isinstance(match, tuple) else match
                events.append({ # logging
                    'Timestamp': pd.Timestamp.now().strftime('%d-%m-%Y %H:%M:%S'),
                    'Filepath': filepath,
                    'Event_Type': 'Neutralization',
                    'Description': f"Pattern-based: '{match_text}' -> '{replacement}'",
                    'Confidence_Score': 1.0,
                    'Details': label
                })
            current = re.sub(pattern, replacement, current, flags=re.IGNORECASE)

    # iterate over each row of the "jobs.csv"
    for _, row in job_table.iterrows():
        target = rf'\b{re.escape(str(row["Original"]))}\b'
        if re.search(target, current, flags=re.IGNORECASE):
            events.append({
               'Timestamp': pd.Timestamp.now().strftime('%d-%m-%Y %H:%M:%S'),
                'Filepath': filepath,
                'Event_Type': 'Neutralization',
                'Description': f"Dictionary: '{row['Original']}' -> '{row['Neutral']}'",
                'Confidence_Score': 1.0,
                'Details': 'Manual Dictionary Match' 
            })
        current = re.sub(target, row["Neutral"], current, flags=re.IGNORECASE)
    
    return current, events

neutralized_jobs = []

for index, row in pre_redacted_table.iterrows():
    original_job = row['Redacted']
    filepath = row['Filepath']

    neu_jobs, new_logs = neutralizer(original_job, filepath)

    neutralized_jobs.append(neu_jobs)
    cumulative_log.extend(new_logs)

pre_redacted_table["Output_final"] = neutralized_jobs 

knio.output_tables[0] = knio.Table.from_pandas(pre_redacted_table)
