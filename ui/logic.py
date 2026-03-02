import re
import hashlib
from collections import defaultdict

# def apply_overlay(text, highlighter_df):
#     from collections import defaultdict
#     import re

#     def get_ui_class(row):
#         # 1. Check for Exclusions
#         if str(row.get('status', '')).lower() == 'exclude':
#             return "pii-excluded"
        
#         # 2. Check if it's a Resolved Gender term
#         # If 'label' doesn't match the standard 'GEN-FL' or 'PERSON' tags, 
#         # it means COALESCE picked up a neutral substitution.
#         lbl = str(row.get('label', ''))
#         cat = str(row.get('category', ''))
#         evt = str(row.get('event_code', ''))
        
#         if evt == 'USR-GIP' or cat == 'GEN-RE' or (cat == 'GEN-FL' and lbl != cat):
#             return "gen-resolved"
        
#         if cat == 'GEN-FL':
#             return "gen-flagged"
            
#         # 3. Default PII Style (Yellow)
#         return "pii-default"
    
#     # Priority: Manual actions (is_manual=1) first, then length
#     highlighter_df['text_len'] = highlighter_df['pii_text'].str.len()
#     highlighter_df['sort_priority'] = highlighter_df['is_manual'].apply(lambda x: 0 if x == 1 else 1)
    
#     sorted_df = highlighter_df.sort_values(
#         by=['sort_priority', 'text_len'], 
#         ascending=[True, False]
#     ).drop_duplicates(subset=['pii_text'])

#     processed_text = text
    
#     for _, r in sorted_df.iterrows():
#         word = r['pii_text']
#         ui_class = get_ui_class(r)

#         is_excluded = str(r.get('status', '')).upper() == 'EXCLUDE'
      
#         # Logic for the arrow suffix:
#         # Show arrow if it's PII (to show the label) 
#         # OR if it's a Gender term that has a custom neutral word
        
#         arrow = ""
#         if not is_excluded:
#             lbl = r['label']
#             is_gender = r['category'] in ['GEN-FL', 'GEN-RE', 'GENDER']
#             has_substitution = lbl != r['category']

#             if not is_gender:
#                 arrow = f" <small>({lbl})</small>"
#             elif is_gender and has_substitution:
#                 arrow = f" <small>→ {lbl}</small>"
        
#         # Global replace with the 'Shield' lookahead
#         #pattern = rf'\b{re.escape(word)}\b(?![^<]*>)'
#         pattern = rf'(?![^<]*>){re.escape(word)}(?![^<]*>)'
#         replacement = f'<mark class="{ui_class}" data-id="{r["pii_id"]}">{word}{arrow}</mark>'
        
#         processed_text = re.sub(pattern, replacement, processed_text)

#     return processed_text

def apply_overlay(text, highlighter_df):
    import re
    from collections import deque

    def get_ui_class(row):
        if str(row.get('status', '')).lower() == 'exclude':
            return "pii-excluded"
        lbl = str(row.get('label', ''))
        cat = str(row.get('category', ''))
        evt = str(row.get('event_code', ''))
        if evt == 'USR-GIP' or cat == 'GEN-RE' or (cat == 'GEN-FL' and lbl != cat):
            return "gen-resolved"
        return "gen-flagged" if cat == 'GEN-FL' else "pii-default"

    # Sort by pii_id to maintain a consistent order of appearance
    sorted_df = highlighter_df.sort_values(by=['pii_id'])

    # Group instances by word
    instances = {}
    for _, row in sorted_df.iterrows():
        word = row['pii_text']
        if word not in instances:
            instances[word] = deque()
        instances[word].append(row)

    def replace_func(match):
        word = match.group(0)
        if word in instances and instances[word]:
            r = instances[word].popleft() # Takes the next 'surgical' instance
            ui_class = get_ui_class(r)
            is_excluded = str(r.get('status', '')).upper() == 'EXCLUDE'
            
            arrow = ""
            if not is_excluded:
                lbl = r['label']
                is_gender = r['category'] in ['GEN-FL', 'GEN-RE', 'GENDER']
                has_sub = lbl != r['category']
                if not is_gender:
                    arrow = f" <small>({lbl})</small>"
                elif is_gender and has_sub:
                    arrow = f" <small>→ {lbl}</small>"
            
            return f'<mark class="{ui_class}" data-id="{r["pii_id"]}">{word}{arrow}</mark>'
        return word

    if not sorted_df.empty:
        # Sort words by length descending to prevent partial matching (e.g., 'Berlin' matching inside 'Berliner')
        all_words = sorted(instances.keys(), key=len, reverse=True)
        pattern_str = '|'.join(map(re.escape, all_words))
        pattern = rf'(?![^<]*>)\b({pattern_str})\b(?![^<]*>)'
        text = re.sub(pattern, replace_func, text)

    return text

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