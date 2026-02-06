import pandas as pd
import knime.scripting.io as knio

audit_df = knio.input_tables[0].to_pandas()

def summarize_compliance(df):
    summary = []

    for filepath in df['Filepath'].unique():
        file_events = df[df['Filepath'] == filepath]

        layout_score = file_events[file_events['Event_type'] == 'Layout_Analysis']['Confidence_Score'].mean()
        if pd.isna(layout_score): layout_score = 1.0

        t2_pii_events = file_events[file_events['Event_type'] == "PII_Detection_T2"]
        if not t2_pii_events.empty:
            n_min = t2_pii_events['Confidence_Score'].min()
        else:
            n_min = 1.0

        trust_score = (min(layout_score, n_min) * 0.8) + (n_min * 0.2)

        status = "PASS" if trust_score > 0.83 else "REVIEW_REQUIRED"

        pii_count = len(file_events[file_events['Event_type'].isin(['PII_Detection_T1', 'PII_Detection_T2'])])
        neutral_count = len(file_events[file_events['Event_type'] == 'Neutralization'])

        summary.append({
            'File': filepath.split('\\')[-1],
            'Layout_Quality': f"{layout_score * 100:.0f}%",
            'PII_Removed': pii_count,
            'Titles_Neutralized': neutral_count,
            'T2_Min_Confidence': f"{n_min*100:.1f}%",
            'Compliance_Grade': status,
            'Trust_Score': trust_score
        })

    return pd.DataFrame(summary)

summary_table = summarize_compliance(audit_df)
knio.output_tables[0] = knio.Table.from_pandas(summary_table)