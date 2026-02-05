import pandas as pd
import knime.scripting.io as knio

input_df = knio.input_tables[0].to_pandas()

def cert_generator(row):
    cert = f"""
==========================================================
CERTIFICATE OF COMPLIANCE: {row['File']}
==========================================================
Date: {pd.Timestamp.now().strftime('%d.%m.%Y')}
Processing ID: COMP-{hash(row['File']) % 10**8}

1. DATA INTEGRITY
- Layout Quality: {row['Layout_Quality']}
- Processing Status: {row['Compliance_Grade']}

2. REDACTION SUMMARY
- Personal Identifiers Removed: {row['PII_Removed']}
- Gender-Neutral Adjustments: {row['Titles_Neutralized']}

3. LEGAL DECLARATION
This document has been processed by Complyable.
PII has been masked using Tier 1 (Regex) and 
Tier 2 (NLP) protocols to ensure compliance with 
the EU AI Act and GDPR.
==========================================================
"""
    return cert

certificate_out = []

for _, row in input_df.iterrows():
    certificate = cert_generator(row)
    certificate_out.append(certificate)

output_df = input_df.copy()
output_df['Certificate_Text'] = certificate_out

knio.output_tables[0] = knio.Table.from_pandas(output_df)