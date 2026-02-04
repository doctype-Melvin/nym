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
        return ""
    
    # Level 0: HEADER DETECTION 
    # Horizontally scan the top 25 % of the page for a valley 
    header_bottom = 0
    top_limit = height * 0.25

    # Sniff out the gaps vertically (aling y-axis)
    y_ranges = []
    for word in [word for word in words if word['bottom'] <= top_limit]:
        y_ranges.append((word['top'], word['bottom']))

    # If there are words at the top, check for a gap below them
    gap_size = 15
    if y_ranges:
        max_y = max(range[1] for range in y_ranges)
        # look for words after a 15 px gap (gap_size)
        lower_words = [word for word in words if word['top'] > max_y + gap_size]
        if lower_words:
            header_bottom = max_y + 5 # buffer

    # Level 1: VERTICAL DENSITY SCAN
    # Scan area below header
    main_content_words = [word for word in words if word['top'] >= header_bottom]

    # horizontal occupancy map
    occupancy = [0] * int(width)
    for word in main_content_words:
        for x in range(int(word['x0']), int(word['x1'])):
            if x < len(occupancy):
                occupancy[x] += 1

    # find the widest vertical gutter
    best_gutter = None
    max_gutter_width = 0
    current_gap_start = None

    # set the search area starting 10 % and 
    # ending 90 % of page width
    start_search = int(width * 0.1)
    end_search = int(width * 0.1)

    for x in range(start_search, end_search):
        if occupancy[x] == 0:
            if current_gap_start is None:
                current_gap_start = x
        else:
            if current_gap_start is not None:
                gap_width = x - current_gap_start
                if gap_width > max_gutter_width and gap_width >= gap_size:
                    max_gutter_width = gap_width
                    best_gutter = (current_gap_start, x)
                current_gap_start = None

    # --- FINAL ASSEMBLY ---
    header_text = ""
    sidebar_text = ""
    body_text = ""

    # 1. Extract Header
    if header_bottom > 0:
        header_text = page.crop((0, 0, width, header_bottom)).extract_text() or ""
    
    # 2. Extract Columns
    if best_gutter:
        gap_start, gap_end = best_gutter
        left_crop = page.crop((0, header_bottom, gap_start, height)).extract_text() or ""
        right_crop = page.crop((0, gap_end, header_bottom, width, height)).extract_text() or ""

        if (gap_start) < (width - gap_end):
            sidebar_text, body_text = left_crop, right_crop
        else: 
            body_text, sidebar_text = left_crop, right_crop
    else: 
        body_text = page.crop((0, header_bottom, width, height)).extract_text() or ""

    sections = [header_text, sidebar_text, body_text]
    return "\n".join([section.strip() for section in sections if section.strip()])
# --- END --- layout analyzing function --- END ---

# ---- UTILITY FN ----
# Remove all unnecessary whitespace and linebreaks from text
clean_text = lambda t:  ' '.join(t.replace('\n', ' ').split())

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
output = []

# Loop over all provided filepaths in dir
for path in input_df['Filepath']:
    if not str(path).lower().endswith('.pdf'):
        output.append(f"SKIPPED: not a PDF {path}")
        continue
    
    # Use pdfplumber to open pdf
    full_resume_text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = analyze_layout_and_extract(page)
            full_resume_text.append(page_text)
    
   
    # Glue the pages back together
    full_content = "\n".join(full_resume_text)

    # --------- Remove all padding empty whitespace ---------------------------
    # 1. Replace all non-breaking spaces (\xa0) and tabs with standard spaces
    clean_content = re.sub(r'[\t\xa0]', ' ', full_content)

    # 2. Line for line gets stripped and finally all empty lines are removed
    lines = [line.strip() for line in clean_content.splitlines()]
    clean_content = "\n".join([l for l in lines if l])
    
    # 3. Get all the remaining unnecessary empty spaces
    full_content = re.sub(r' +', ' ', clean_content).strip()
    
        
    output.append(full_content)

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_df['Filepath'],
    "Content": output,
    }))