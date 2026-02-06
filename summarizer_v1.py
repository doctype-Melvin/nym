import pandas as pd
import knime.scripting.io as knio

# Port 0 should be your cumulative_log from the Neutralizer node
audit_df = knio.input_tables[0].to_pandas()

def summarize_compliance(df):
    summary = []

    for filepath in df['Filepath'].unique():
        file_events = df[df['Filepath'] == filepath]

        # 1. ANALYZER METRIC (Tier 0)
        layout_score = file_events[file_events['Event_type'] == 'Layout_Analysis']['Confidence_Score'].mean()
        if pd.isna(layout_score): layout_score = 1.0

        # 2. AI NER METRIC (Tier 2)
        t2_events = file_events[file_events['Event_type'] == "PII_Detection_T2"]
        n_min = t2_events['Confidence_Score'].min() if not t2_events.empty else 1.0

        # 3. NEUTRALIZATION METRIC (Tier 3)
        # Even though current scores are 1.0, we include this for SLM-readiness
        t3_events = file_events[file_events['Event_type'] == "Neutralization"]
        t3_min = t3_events['Confidence_Score'].min() if not t3_events.empty else 1.0

        # 4. PESSIMISTIC MATH (The "Weakest Link" Logic)
        # We find the absolute lowest confidence across all AI/Layout steps
        weakest_link = min(layout_score, n_min, t3_min)
        
        # Weighted formula: Heavily penalize the weakest link
        trust_score = (weakest_link * 0.8) + (n_min * 0.2)

        # 5. DYNAMIC COMPLIANCE STATUS
        # threshold 0.83 as per your previous requirement
        status = "PASS" if trust_score > 0.83 else "REVIEW_REQUIRED"

        # 6. PRODUCTIVITY COUNTS
        pii_count = len(file_events[file_events['Event_type'].isin(['PII_Detection_T1', 'PII_Detection_T2'])])
        neutral_count = len(t3_events)

        # Handle filepath strings for different OS (Windows/Linux)
        display_name = filepath.split('\\')[-1].split('/')[-1]

        summary.append({
            'File': display_name,
            'PII_Redacted': pii_count,
            'Titles_Neutralized': neutral_count,
            'Layout_Quality': f"{layout_score * 100:.0f}%",
            'AI_Certainty': f"{n_min * 100:.1f}%",
            'Trust_Score': round(trust_score, 4),
            'Compliance_Grade': status
        })

    return pd.DataFrame(summary)

summary_table = summarize_compliance(audit_df)
knio.output_tables[0] = knio.Table.from_pandas(summary_table)