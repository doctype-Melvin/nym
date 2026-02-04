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

    return "\n".join(glued)
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