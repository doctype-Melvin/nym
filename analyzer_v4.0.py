import knime.scripting.io as knio
import pdfplumber
import pandas as pd
import re

# --- START --- Layout Analyzer --- 
def layout_analyzer(page):
    width = page.width
    height = page.height
    words = page.extract_words()
    
    if not words:
        return {'content': "", 'confidence': 1.0, 'strategy': 'Empty_page', 'jumps': 0}
    
    # --- 0. Chaos detection (non-typical layouts) ---
    # contains a pre-check decision tree to call corresponding worker functions
    total_jumps = 0
    last_y = 0
    for word in words:
        if word['top'] < (last_y - 15): # jump to next word is more than 15px
            total_jumps += 1
        last_y = word['top']
    
    # --- 1. Classification ---
    x_starts = [word['x0'] for word in words] # look for clustering

    # Split page in half to determin density
    left_half = [x for x in x_starts if x < width * 0.5]
    right_half = [x for x in x_starts if x > width * 0.5]

    # Decision logic
    if total_jumps > (len(words) * 0.1): #more than 10% are out of order (chaotic)
        strategy = "Creative_layout_detected"
        content = reconstruct_with_lines(words)
        conf = 0.65

    elif len(left_half) > (len(words) * 0.15) and len(right_half) > (len(words)*0.15):
        strategy = "Sidebar_detected"
        content = extract_as_sidebar(words, width, height)
        conf = 0.9
    else: 
        strategy = "Single_column"
        content = extract_as_single_column(words)
        conf = 0.97
    
    return {
        'content': content,
        'confidence': conf,
        'strategy': strategy,
        'jumps': total_jumps
    }

def extract_as_single_column(words):
    if not words: return ""
    return reconstruct_with_lines(words)

def extract_as_sidebar(words, width, height):
    mid_points = sorted([word['x0'] for word in words if width * 0.1 < word['x0'] < width * 0.9])

    if len(mid_points) < 2:
        return reconstruct_with_lines(words) # Fallback to single col
    
    # Get largest gap between word and starts
    gaps = []
    for i in range(len(mid_points) -1 ):
        gap_size = mid_points[i+1] - mid_points[i]
        center = (mid_points[i+1] + mid_points[i]) / 2
        gaps.append((gap_size, center))
    
    max_gap, split_x = max(gaps, key=lambda x: x[0])

    if max_gap < 10:
        return reconstruct_with_lines(words)

    # Word split 
    left_words = [word for word in words if word['x0'] < split_x]
    right_words = [word for word in words if word['x0'] >= split_x]

    # Reconstruction
    left_text = reconstruct_with_lines(left_words)
    right_text = reconstruct_with_lines(right_words)

    if len(left_words) < len(right_words):
        return f"-- Sidebar --\n{left_text}\n\n-- Main --\n{right_text}"
    else: 
        return f"-- Main --\n{left_text}\n\n-- Sidebar --\n{right_text}"

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
    
    current_full_content = ""
    avg_score = 0
    final_strategies = "N/A"
    jumps_count = 0
    
    try:
        page_contents = []
        page_scores = []
        page_strategies = []
        total_jumps = 0
        
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                res = layout_analyzer(page)
                page_contents.append(res['content'])
                page_scores.append(res['confidence'])
                page_strategies.append(res['strategy'])
                total_jumps += res.get('jumps', 0)
        
        # Aggregate data
        raw_content = "\n\n".join(page_contents)
        avg_score = sum(page_scores) / len(page_scores) if page_scores else 0
        final_strategies = ", ".join(list(set(page_strategies)))
        jumps_count = total_jumps

        # Post-processing (TitleCase and Cleanup)
        clean_content = re.sub(r'[\t\xa0]', ' ', raw_content)
        processed_lines = []
        for line in clean_content.splitlines():
            if line.strip():
                processed_lines.append(to_titlecase(line.strip()))
        
        current_full_content = "\n".join(processed_lines)
        
        output.append({
            'Filepath': path,
            'Content': current_full_content,
            'status': 'success',
            'layout_conf_score': avg_score
        })

    except Exception as e:
        # This will now show you the ACTUAL Python error (e.g., NameError, TypeError)
        import traceback
        error_msg = f"Error: {str(e)} | Trace: {traceback.format_exc()[:100]}"
        output.append({
            'Filepath': path, 
            'Content': error_msg, 
            'status': 'failed', 
            'layout_conf_score': 0
        })

    # Always log to audit, using whatever data we successfully gathered
    audit_log.append({
        'Timestamp': pd.Timestamp.now().strftime('%d.%m.%Y %H:%M:%S'),
        'Filepath': path,
        'Event_type': 'Layout_Analysis',
        'Description': f"Strategies: {final_strategies}",
        'Confidence_Score': avg_score,
        'Details': f"Total Jumps: {jumps_count}"
    })

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame(output))
knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(audit_log))