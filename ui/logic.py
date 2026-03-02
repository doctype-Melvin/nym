import re
import hashlib
from collections import defaultdict

def apply_overlay(text, highlighter_df):
    #Injects <mark> tags into the text based on database detections
    render_counts = defaultdict(int)

    def get_ui_class(row):
        if str(row['status']).lower() == 'exclude':
            return "pii-excluded"
        lbl = str(row['category'])
        if lbl == "GEN-RE": return "gen-resolved"
        if lbl == "GEN-FL": return "gen-flagged"
        return "pii-default"
    
    # Priority sorting: ensures Neutralized (GEN-RE) takes precedence
    highlighter_df['priority'] = highlighter_df['category'].apply(
        lambda x: 1 if x == "GEN-RE" else (2 if x == "GEN-FL" else 3)
    )
    sorted_df = highlighter_df.sort_values(by=['pii_text', 'occurrence_index', 'priority'])
    highlighter_df = sorted_df.drop_duplicates(subset=['pii_text', 'occurrence_index'], keep='first')

    processed_text = text
    for word, group in highlighter_df.groupby('pii_text'):
        render_counts[word] = 0 
        pattern = rf'(?<!\w){re.escape(word)}(?!\w)'
        
        def count_and_replace(match):
            render_counts[word] += 1
            match_row = group[group['occurrence_index'] == render_counts[word]]
            
            if not match_row.empty:
                r = match_row.iloc[0]
                ui_class = get_ui_class(r)
                lbl = r['label']
                arrow = f" <small>→ {lbl}</small>" if lbl not in ["GEN-RE", "GEN-FL", "GENDER"] else ""
                return f'<mark class="{ui_class}" data-id="{r["pii_id"]}">{match.group(0)}{arrow}</mark>'
            
            return match.group(0)

        processed_text = re.sub(pattern, count_and_replace, processed_text)

    return processed_text

def generate_live_redaction(text, highlighter_df):
    #Produces the AI-ready version of the text with [LABEL] placeholders.
    if not text or highlighter_df.empty:
        return text
    
    to_redact = highlighter_df[highlighter_df['status'] == 'REDACT'].copy()
    to_redact['len'] = to_redact['pii_text'].str.len()
    to_redact = to_redact.sort_values('len', ascending=False)

    processed_text = text
    for _, row in to_redact.iterrows():
        word = row['pii_text']
        label = row['category'] if row['category'] else 'PII'
        pattern = rf'\b{re.escape(word)}\b'
        replacement = f'**[{label.upper()}]**'
        processed_text = re.sub(pattern, replacement, processed_text)
    
    return processed_text

def create_pii_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()