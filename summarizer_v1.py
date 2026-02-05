import pandas as pd
import knime.scripting.io as knio

audit_df = knio.input_tables[0].to_pandas()

def summarize_compliance(df):
    summary = []

    for filepath in df['Filepath'].unique():
        file_events = df[df['Filepath'] == filepath]

        layout_score = file_events[file_events['Event_type'] == 'Layout_Analysis']['Confidence_Score'].mean()
        pii_count = len(file_events[file_events['Event_type'].isin(['PII_Detection_T1', 'PII_Detection_T2'])])
        neutral_count = len(file_events[file_events['Event_type'] == 'Neutralization'])

        final_trust = round(layout_score, 2)

        summary.append({
            'File': filepath.split('\\')[-1],
            'Layout_Quality': f"{layout_score * 100:.0f}%",
            'PII_Removed': pii_count,
            'Titles_Neutralized': neutral_count,
            'Compliance_Grade': "PASS" if final_trust > 0.7 else "REVIEW_REQUIRED",
            'Trust_Score': final_trust
        })

    return pd.DataFrame(summary)

summary_table = summarize_compliance(audit_df)
knio.output_tables[0] = knio.Table.from_pandas(summary_table)