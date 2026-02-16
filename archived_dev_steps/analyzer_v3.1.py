import knime.scripting.io as knio
import pdfplumber
import pandas as pd
import re

# --- START --- layout analyzing function --- START ---
def analyze_layout_and_extract(page):
    width = page.width
    height = page.height
    words = page.extract_words()
    
    if not words:
        return {'content': "", 'confidence': 1.0, 'jumps': 0, 'noise': 0}

    # --- 1. COORDINATE SORTING ---
    # Sort primarily by 'top' (Y) then 'x0' (X)
    words.sort(key=lambda w: (w['top'], w['x0']))

    # --- 2. NOISE & JUMP AUDIT ---
    total_jumps = 0
    noise_count = 0
    last_y = 0
    noise_chars = ['ñ', '¶', 'ÿ']
    
    for word in words:
        if any(c in word['text'] for c in noise_chars):
            noise_count += 1
        if word['top'] < (last_y - 10):
            total_jumps += 1
        last_y = word['top']

    # --- 3. SPATIAL SEGMENTATION ---
    header_limit = height * 0.15
    h_words = [w for w in words if w['bottom'] <= header_limit]
    
    best_x = width * 0.3
    b_words = [w for w in words if w['bottom'] > header_limit and w['x0'] >= best_x]
    s_words = [w for w in words if w['bottom'] > header_limit and w['x0'] < best_x]

    # Reconstruct with preserved line breaks
    header_text = reconstruct_with_lines(h_words)
    sidebar_text = reconstruct_with_lines(s_words)
    body_text = reconstruct_with_lines(b_words)

    # --- 4. SCORING ---
    jump_penalty = (total_jumps / (len(words) * 0.1)) if len(words) > 0 else 0
    noise_penalty = (noise_count * 0.1)

    complexity_penalty = 0
    if len(s_words) > 5 and len(b_words) > 5:
        complexity_penalty = 0.05 # accounts for multi-column layouts

    layout_confidence = round(max(0, 1.0 - jump_penalty - noise_penalty - complexity_penalty), 2)

    sections = [header_text, sidebar_text, body_text]
    glued = [section.strip() for section in sections if section.strip()]

    return {
        'content': "\n\n".join(glued), # Double newline to separate segments
        'confidence': layout_confidence,
        'jumps': total_jumps,
        'noise': noise_count
    }

# ---- UTILITY FN ----
clean_text = lambda t: ' '.join(t.replace('\n', ' ').split())

# --- 3. VERTICAL BINNING HELPER ---
def reconstruct_with_lines(word_list):
    if not word_list: return ""
    # Sort words by top again just to be safe
    word_list.sort(key=lambda w: (w['top'], w['x0']))
    
    lines = []
    if not word_list: return ""
    
    current_line = [word_list[0]['text']]
    last_top = word_list[0]['top']
    
    for i in range(1, len(word_list)):
        w = word_list[i]
        # If the word is within 4 pixels of the previous word's top, it's the same line
        if abs(w['top'] - last_top) < 4:
            current_line.append(w['text'])
        else:
            lines.append(" ".join(current_line))
            current_line = [w['text']]
            last_top = w['top']
    
    lines.append(" ".join(current_line)) # Add the last line
    return "\n".join(lines)

def to_titlecase(text):
    def replace_match(match):
        word = match.group(0)
        return word.title() if len(word) >= 4 else word
    return re.sub(r'\b[A-ZÜÖÄß]{2,}\b', replace_match, text)

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
output = []
audit_log = []

for path in input_df['Filepath']:
    if not str(path).lower().endswith('.pdf'):
        output.append({'Filepath': path, 'Content': "SKIPPED", 'status': 'skipped', 'layout_conf_score': 0})
        continue
    
    try:
        full_resume_text = []
        all_page_score = []
        total_file_jumps = 0
        total_file_noise = 0
        
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                result = analyze_layout_and_extract(page)
                full_resume_text.append(result['content'])
                all_page_score.append(result['confidence'])
                total_file_jumps += result['jumps']
                total_file_noise += result['noise']
        
        full_content = "\n".join(full_resume_text)
        avg_confidence_score = sum(all_page_score) / len(all_page_score) if all_page_score else 0

        # Post-processing
        clean_content = re.sub(r'[\t\xa0]', ' ', full_content)
        lines = [to_titlecase(line.strip()) for line in clean_content.splitlines() if line.strip()]
        full_content = "\n".join(lines)
        full_content = re.sub(r' +', ' ', full_content).strip()
        
        output.append({
            'Filepath': path,
            'Content': full_content,
            'status': 'success',
            'layout_conf_score': avg_confidence_score
        })

        # --- UPDATED AUDIT LOG ---
        audit_log.append({
            'Timestamp': pd.Timestamp.now().strftime('%d.%m.%Y %H:%M:%S'),
            'Filepath': path,
            'Event_type': 'Layout_Analysis',
            'Description': f"Spatial Audit: {total_file_jumps} jumps, {total_file_noise} noise artifacts.",
            'Start': None,
            'End': None,
            'Confidence_Score': avg_confidence_score,
            'Details': f"Sidebar segmentation with {total_file_jumps} reading-order jumps detected."
        })
    except Exception as e:
        output.append({'Filepath': path, 'Content': str(e), 'status': 'failed', 'layout_conf_score': 0})

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame(output))
knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(audit_log))