import re
import hashlib
from collections import defaultdict
from datetime import datetime
import os
from fpdf import FPDF
from pathlib import Path
import subprocess
import platform

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "output"

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

            is_gender = r['event_code'] == 'T3-GIP' or r['category'] in ['GEN-FL', 'GEN-RE', 'GENDER']
            
            if is_gender and not is_excluded:
                display_text = f"{word} <small> → ({r['label']})</small>"
            else:
                display_text = f"{word} <small>({r['label']})</small>"
            
            return f'<mark class="{ui_class}" data-id="{r["pii_id"]}">{display_text}</mark>'
        return word

    if not sorted_df.empty:
        # Sort words by length descending to prevent partial matching (e.g., 'Berlin' matching inside 'Berliner')
        all_words = sorted(instances.keys(), key=len, reverse=True)
        pattern_str = '|'.join(map(re.escape, all_words))
        pattern = rf'(?![^<]*>)(?<!\w)({pattern_str})(?!\w)(?![^<]*>)'
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

def generate_final_sanitized_text(original_text, highlighter_df):
    import re
    # 1. Only get rows where status != 'EXCLUDE'
    active_df = highlighter_df[highlighter_df['status'].str.upper() != 'EXCLUDE']
    
    # 2. Sort words by length descending to prevent partial matching
    sorted_words = sorted(active_df['pii_text'].unique(), key=len, reverse=True)
    
    final_text = original_text
    for word in sorted_words:
        # Find the label (substitution) for this word from the DF
        # Assuming one substitution per unique word for the final export
        substitution = active_df[active_df['pii_text'] == word]['label'].iloc[0]
        
        # Surtically replace with the neutral title or [REDACTED] label
        pattern = rf'(?<!\w){re.escape(word)}(?!\w)'
        final_text = re.sub(pattern, substitution, final_text)
        
    return final_text

def create_pii_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def clean_for_pdf(text):
    return text.encode("latin-1", "ignore").decode("latin-1")

def generate_pdf_certificate(filepath, user_id, audit_id, save_path):
    
    filename = os.path.basename(filepath)
    pdf_path = save_path

    # 2. Create PDF Object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    # 3. Header & Branding
    pdf.cell(0, 10, "Complyable: Certificate of Redaction", ln=True, align='C')
    pdf.ln(10)

    # 4. Certificate Body (The Evidence)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Audit ID: {audit_id}", ln=True)
    pdf.cell(0, 10, f"Original File: {filename}", ln=True)
    pdf.cell(0, 10, f"Certified By: {user_id}", ln=True)
    pdf.cell(0, 10, f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 10, "This document confirms that the original file was processed according to EU AI Act compliance standards. All personal identifying information (PII) has been redacted or neutralized before being passed to AI processing modules.")

    # 5. Save Output
    pdf.output(pdf_path)
    return pdf_path

def generate_redacted_pdf(sanitized_text, save_path):
    safe_text = clean_for_pdf(sanitized_text)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # multi_cell handles line breaks automatically
    # w=0 means it stretches to the right margin
    pdf.multi_cell(0, 8, safe_text)
    
    pdf.output(str(save_path))
    return save_path

def open_folder(path):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return False
    
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(['xdg-open', path])
    return True