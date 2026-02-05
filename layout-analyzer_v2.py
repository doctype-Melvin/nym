import knime.scripting.io as knio
import pdfplumber
import pandas as pd
import re

# --- START --- layout analyzing function --- START ---
# v2: This fn scans for top header information,
# detects sidebars and puts their content before
# adding the main content of the document

def analyze_layout_and_extract(page):

    width = page.width
    height = page.height
    words = page.extract_words()
    if not words:
        return {'content': "", 'confidence': 1.0}
    
    # Level 0: HEADER DETECTION 
    header_limit = height * 0.15
    main_words = [word for word in words if word['bottom'] > header_limit]

    # Level 1: Find the gutter
    # search middle 60% to find any consistent gaps
    search_start = int(width * 0.2)
    search_end = int(width * 0.8)

    best_x = width * 0.3
    min_intersections = float('inf')

    for x in range(search_start, search_end, 5): # scan every 5 px
        intersections = sum(1 for word in main_words if word['x0'] < x < word['x1'])

        if intersections <= min_intersections:
            min_intersections = intersections
            best_x = x
            if intersections == 0: break # gap found

    # Include confidence scoring for layout recognition
    # based on found word intersections
    total_word_count = len(main_words) if main_words else 1

    layout_confidence = round(max(0, 1.0 - (min_intersections / ( total_word_count * 0.1 ))), 2)

    # Get the three sections header, sidebar, body
    header_text = page.crop((0, 0, width, header_limit)).extract_text() or ""

    # Left and right are defined by best_x (the gutter)
    left_side = page.crop((0, header_limit, best_x, height)).extract_text() or ""
    right_side = page.crop((best_x, header_limit, width, height)).extract_text() or ""

    if len(left_side) < len(right_side):
        sidebar_text, body_text = left_side, right_side
    else: 
        body_text, sidebar_text = left_side, right_side

    # Put the sections together
    sections = [header_text, sidebar_text, body_text]
    glued = [section.strip() for section in sections if section.strip()]

    return {
        'content': "\n".join(glued),
        'confidence': layout_confidence
    }
# --- END --- layout analyzing function --- END ---

# ---- UTILITY FN ----
# Remove all unnecessary whitespace and linebreaks from text
clean_text = lambda t:  ' '.join(t.replace('\n', ' ').split())

# Transform uppercase to titlecase
def to_titlecase(text):
    def replace_match(match):
        word = match.group(0)
        return word.title() if len(word) >= 4 else word

    return re.sub(r'\b[A-ZÜÖÄß]{2,}\b', replace_match, text)

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
output = [] # all the text content goes here
audit_log = []


# Loop over all provided filepaths in dir
for path in input_df['Filepath']:
    if not str(path).lower().endswith('.pdf'):
        output.append({
            'Filepath': path,
            'Content': f"SKIPPED: not a PDF {path}",
            'status': 'skipped',
            'layout_conf_score': 0
            })
        continue
    
    try:
    # Use pdfplumber to open pdf
        full_resume_text = []
        all_page_score = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                result = analyze_layout_and_extract(page)

                if isinstance(result, dict):
                    page_text = result.get('content', "")
                    score_layout = result.get('confidence', 0.0)
                else:
                    # Fallback if somehow a string still gets through
                    page_text = str(result)
                    score_layout = 0.0
                
                full_resume_text.append(page_text)
                all_page_score.append(score_layout)
        
        # Glue the pages back together
        full_content = "\n".join(full_resume_text)

        # calculate average layout confidence score
        avg_confidence_score = sum(all_page_score) / len(all_page_score) if all_page_score else 0

        # --------- Remove all padding empty whitespace ---------------------------
        # 1. Replace all non-breaking spaces (\xa0) and tabs with standard spaces
        clean_content = re.sub(r'[\t\xa0]', ' ', full_content)

        # 2. Line for line gets stripped and finally all empty lines are removed
        #lines = [line.strip() for line in clean_content.splitlines()]
        lines = []
        for line in clean_content.splitlines():
            stripped = line.strip()
            if stripped:
                processed_line = to_titlecase(stripped)
                lines.append(processed_line)

        clean_content = "\n".join(lines)
        
        # 3. Get all the remaining unnecessary empty spaces
        full_content = re.sub(r' +', ' ', clean_content).strip()
        
        output.append({'Filepath': path,
                        'Content': full_content,
                        'status': 'success',
                        'layout_conf_score': avg_confidence_score})
        audit_log.append({
            'Timestamp': pd.Timestamp.now().strftime('%D.%m.%Y %H:%M:%S'),
            'Filepath': path,
            'Event_type': 'Layout_Analysis',
            'Description': 'Document layout segmented into Header/Sidebar/Body',
            'Start': None,
            'End': None,
            'Confidence_Score': avg_confidence_score,
            'Details': f"Avg intersections: {sum(all_page_score)/len(all_page_score):.2f}"
        })
    except Exception as e:
        output.append({'Filepath': path,
                        'Content':str(e),
                        'status': 'failed',
                        'layout_conf_score': 1})

output_df = pd.DataFrame(output)
knio.output_tables[0] = knio.Table.from_pandas(output_df)

audit_df = pd.DataFrame(audit_log)
knio.output_tables[1] = knio.Table.from_pandas(audit_df)