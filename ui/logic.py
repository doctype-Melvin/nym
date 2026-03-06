import re
import hashlib
from collections import defaultdict
from datetime import datetime
import os
from fpdf import FPDF
from pathlib import Path
import subprocess
import platform
from pipeline import run_pipeline
import unicodedata

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "output"
INPUT_DIR = BASE_DIR / "data" / "input"
WORKFLOW_PATH = BASE_DIR / "knime"
KNIME_EXE = os.getenv("KNIME_PATH", r"/Applications/KNIME 5.4.2.app/Contents/MacOS/knime")
UNICODE_FONT = os.getenv('FONT_PATH', '/Library/Fonts/Arial Unicode.ttf')

def apply_overlay(text, highlighter_df):
    import re
    from collections import deque

    def get_ui_class(row):
        if str(row.get('status', '')).lower() == 'exclude':
            return "pii-excluded"
        lbl = str(row.get('label', ''))
        cat = str(row.get('category', ''))
        evt = str(row.get('event_code', ''))
        if evt in ('USR-GIP', 'T3-GIP') or cat == 'GEN-RE':
            return "gen-resolved"
        return "gen-flagged" if (cat == 'GEN-FL' or evt == 'T3-FLG') else "pii-default"

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

def clean_for_pdf(text):
    if not text:
        return ""
    return re.sub(r'[\uf000-\uf8ff]', '', text)

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

def strip_ui_labels(text):
    #Purges UI-injected markers so we can match the raw document text
    if not text:
        return text
    # Removes " → (LABEL)" and any HTML tags like <small>
    clean = re.sub(r'\s*→\s*\(.*?\)', '', text)
    clean = re.sub(r'<[^>]*>', '', clean)
    return clean.strip()

def generate_final_sanitized_text(original_text, highlighter_df):
    import re
    if not original_text:
        return ""
    if highlighter_df is None or highlighter_df.empty:
        return original_text 
    # 1. Only get rows where status != 'EXCLUDE'
    active_df = highlighter_df[highlighter_df['status'].str.upper() != 'EXCLUDE']
    
    # 2. Sort words by length descending to prevent partial matching
    sorted_words = sorted(active_df['pii_text'].unique(), key=len, reverse=True)
    
    final_text = original_text
    for word in sorted_words:
        row = active_df[active_df['pii_text'] == word].iloc[0]
        category = row.get('category', '')

        if category == 'GEN-FL':
            continue
        # Find the label (substitution) for this word from the DF
        # Assuming one substitution per unique word for the final export
        substitution = active_df[active_df['pii_text'] == word]['label'].iloc[0]
        
        # Surtically replace with the neutral title or [REDACTED] label
        pattern = rf'(?<!\w){re.escape(word)}(?!\w)'
        final_text = re.sub(pattern, substitution, final_text)
        
    return final_text

def create_pii_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def generate_pdf_certificate(filepath, user_id, audit_id, save_path):
    filename = os.path.basename(filepath)
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('ArialUnicode', '', UNICODE_FONT, uni=True)
    pdf.set_font('ArialUnicode', size=16)
    pdf.cell(0, 10, "Complyable: Certificate of Redaction", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('ArialUnicode', size=12)
    pdf.cell(0, 10, f"Audit ID: {audit_id}", ln=True)
    pdf.cell(0, 10, f"Original File: {filename}", ln=True)
    pdf.cell(0, 10, f"Certified By: {user_id}", ln=True)
    pdf.cell(0, 10, f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)
    pdf.set_font('ArialUnicode', size=10)
    pdf.multi_cell(0, 10, "This document confirms that the original file was processed according to EU AI Act compliance standards. All personal identifying information (PII) has been redacted or neutralized before being passed to AI processing modules.")
    pdf.output(str(save_path))
    return save_path

def generate_redacted_pdf(sanitized_text, save_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('ArialUnicode', '', UNICODE_FONT, uni=True)
    pdf.set_font('ArialUnicode', size=11)
    safe_text = clean_for_pdf(sanitized_text or "")
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
        pass
    return True

def stage_uploaded_file(uploaded_file): # copy uploaded file to input folder
    os.makedirs(INPUT_DIR, exist_ok=True)
    target_path = INPUT_DIR / uploaded_file.name

    with open(target_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    
    return str(target_path)

# def trigger_knime():
#     #KNIME_EXE = r"/Applications/KNIME 5.4.2.app/Contents/Eclipse/knime" 
#     # input_abs_path = os.path.abspath(INPUT_DIR)
#     input_abs_path = INPUT_DIR
  

#     cmd = [
#         KNIME_EXE,
#         "-nosplash",
#         "-consolelog",
#         "-application", "org.knime.product.KNIME_BATCH_APPLICATION",
#         "-workflowFile=" + str(WORKFLOW_PATH / "core-v1.knwf"),
#         "-reset",
#         f"-workflow.variable=input_folder_path,{input_abs_path},String"
#     ]

#     try:
#         # Run and wait for it to finish
#         result = subprocess.run(cmd, capture_output=True, text=True, check=True)
#         return True, result.stdout
#     except subprocess.CalledProcessError as e:
#         return False, e.stderr
#     except subprocess.TimeoutExpired:
#         return False, f"Knime time out"

def trigger_pipeline(dir):
   return run_pipeline(dir)