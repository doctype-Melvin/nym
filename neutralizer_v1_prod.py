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

def neutralizer(text):

    # catches: Bankkaufmann, Bürokauffrau, Einzelhandelskauffrau, etc.
    kaufmann_pattern = r"\b(\w+)(kaufmann|kauffrau)\b"
    text = re.sub(kaufmann_pattern, r"\1kaufleute", text, flags=re.IGNORECASE)

    # the "Kaufmann für..." case
    kaufmann_fur_pattern = r"\b(Kaufmann|Kauffrau)\s+für\b"
    text = re.sub(kaufmann_fur_pattern, "Fachkraft für", text, flags=re.IGNORECASE)

    # the "Kaufmann ..." case
    kaufmann_fur_pattern = r"\b(Kaufmann|Kauffrau)\s\b"
    text = re.sub(kaufmann_fur_pattern, "Fachkraft ", text, flags=re.IGNORECASE)
    current = str(text)

    # iterate over each row of the "berufsbezeichnungen_index.csv"
    for _, row in job_table.iterrows():
        target = rf'\b{re.escape(str(row["Original"]))}\b'
        current = re.sub(target, row["Neutral"], current, flags=re.IGNORECASE)
    
    return current

pre_redacted_table["Neutral"] = pre_redacted_table["Redacted"].apply(neutralizer) 

knio.output_tables[0] = knio.Table.from_pandas(pre_redacted_table)
