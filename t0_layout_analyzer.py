import knime.scripting.io as knio
import pdfplumber
import pandas as pd
import re
import datetime

# --- START --- Layout Analyzer --- 
def play_analyzer(page):
    """
    Smoke tests for layout complexity.
    Returns a score between 0.0 (Simple) and 1.0 (Chaotic).
    """
    words = page.extract_words()
    if not words: return 0.0, 0
    
    # 1. Fragment Density: High word count in small boxes = complex layout
    # (Typical Canva/Designer PDFs where every line is its own object)
    fragmentation = len(words) / 100 

    # 2. Vertical Entropy: How many different left-margin start points?
    # Standard docs have ~5-10. Chaos docs have 40+.
    x_starts = [round(w['x0']) for w in words]
    unique_starts = len(set(x_starts))
    entropy = unique_starts / 40 

    # 3. Collision Risk: Very basic check for overlapping X-ranges
    # Just average the fragmentation and entropy for a reliable heuristic
    risk_score = round(min(1.0, max(0.0, (fragmentation + entropy) / 2)), 2)
    return risk_score, len(words)


input_df = knio.input_tables[0].to_pandas()
output = []
audit_log = []

for _, row in input_df.iterrows():
    path = row['Filepath']

    if not str(path).lower().endswith('.pdf'):

        output.append({
            'filepath': path,
            'layout_score': 0.0,
            'status': 'skipped'
            })
        continue 
    
    work_start = datetime.datetime.now()
    risk_score = 0.5
    word_count = 0
    status = 'success'
    
    try:
        with pdfplumber.open(path) as pdf:
            page_scores = []
            for page in pdf.pages:
                page_score, page_words = play_analyzer(page)
                page_scores.append(page_score)
                word_count += page_words

            risk_score = sum(page_scores) / len(page_scores) if page_scores else 0
            
    except Exception as e:
        status = f'failed: {str(e)[:50]}'
        risk_score = 1.0 # Max risk if can't even open it
    
    # Output for pipeline and DB writer
    output.append({
        'filepath': path, 
        'layout_score': risk_score, 
        'status': status
    })

    # Processing Log
    audit_log.append({
        'Timestamp': datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        'Filepath': path,
        'Layout_score': risk_score,
        'Word_count': word_count,
        'Processing_time': (datetime.datetime.now() - work_start).total_seconds(),
        'Status': status
    })

# Output to KNIME
knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame(output))
knio.output_tables[1] = knio.Table.from_pandas(pd.DataFrame(audit_log))