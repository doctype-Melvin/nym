import pandas as pd
import knime.scripting.io as knio

# Port 0 should be your cumulative_log from the Neutralizer node
audit_df = knio.input_tables[0].to_pandas()

def summarize_compliance(df):
    summary = []

    for filepath in df['filepath'].unique():
        file_events = df[df['filepath'] == filepath]

        # 1. ANALYZER METRIC (Tier 0)
        layout_score = file_events[file_events['event_code'] == 'T0-ANL']['confidence_score'].mean()
        if pd.isna(layout_score): layout_score = 1.0

        # 2. PII METRIC (T1 + T2) - Use .isin() for "OR" logic
        pii_codes = ["T1-RGX", "T2-NER"]
        pii_events = file_events[file_events['event_code'].isin(pii_codes)]
        t2_min = pii_events['confidence_score'].min() if not pii_events.empty else 1.0

        # 3. NEUTRALIZATION METRIC (Tier 3)
        gip_codes = ["T3-GIP", "T3-FLG"]
        t3_events = file_events[file_events['event_code'].isin(gip_codes)]
        t3_min = t3_events['confidence_score'].min() if not t3_events.empty else 1.0

        # 4. PESSIMISTIC MATH
        # We take the lowest confidence found in the entire document pipeline
        weakest_link = min(layout_score, t2_min, t3_min)
        
        # Weighted formula: Heavily penalize the weakest link (The "Chain" logic)
        # If any PII was missed or uncertain, the trust score drops sharply.
        trust_score = (weakest_link * 0.8) + (t2_min * 0.2)

        # 5. DYNAMIC COMPLIANCE STATUS
        status = "PASS" if trust_score > 0.85 else "REVIEW_REQUIRED"

        # 6. PRODUCTIVITY COUNTS
        pii_count = len(pii_events)
        neutral_count = len(t3_events)

        # Handle filepath strings
        display_name = filepath.split('\\')[-1].split('/')[-1]

        summary.append({
            'file': display_name,
            'pii_redacted': pii_count,
            'gip': neutral_count,
            'layout_quality': f"{layout_score * 100:.0f}%",
            'ai_certainty': f"{t2_min * 100:.1f}%",
            'trust_score': round(trust_score, 4),
            'compliance_grade': status
        })

    return pd.DataFrame(summary)

summary_table = summarize_compliance(audit_df)
knio.output_tables[0] = knio.Table.from_pandas(summary_table)