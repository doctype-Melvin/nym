import re
import hashlib
from collections import defaultdict

def apply_overlay(text, highlighter_df):
    from collections import defaultdict
    import re

    def get_ui_class(row):
        if str(row.get('status', '')).lower() == 'exclude':
            return "pii-excluded"
        lbl = str(row.get('category', ''))
        evt = str(row.get('event_code', ''))
        if lbl == "GEN-RE" or evt == 'USR-GIP': return "gen-resolved"
        if lbl == "GEN-FL": return "gen-flagged"
        return "pii-default"
    
    # 1. PRIORITY: Sort by Manual status, then by length (Longest first)
    highlighter_df['text_len'] = highlighter_df['pii_text'].str.len()
    highlighter_df['sort_priority'] = highlighter_df['is_manual'].apply(lambda x: 0 if x == 1 else 1)
    
    # group by text to handle each unique word/phrase once
    # Longest wins - assuming user selection includes system detection
    sorted_df = highlighter_df.sort_values(
        by=['sort_priority', 'text_len'], 
        ascending=[True, False]
    ).drop_duplicates(subset=['pii_text'])

    processed_text = text
    
    for _, r in sorted_df.iterrows():
        word = r['pii_text']
        ui_class = get_ui_class(r)
        lbl = r['label']
        arrow = f" <small>→ {lbl}</small>" if lbl not in ["GEN-RE", "GEN-FL", "GENDER"] else ""
        
        # 2. THE PATTERN: 
        # \b word boundaries
        # (?![^<]*>) Negative lookahead: "Don't match if the next bracket is a closing one"
        # This prevents 'Erzieher' from matching if it's already inside '<mark>Erzieher</mark>'
        pattern = rf'\b{re.escape(word)}\b(?![^<]*>)'
        
        replacement = f'<mark class="{ui_class}" data-id="{r["pii_id"]}">{word}{arrow}</mark>'
        
        processed_text = re.sub(pattern, replacement, processed_text)

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