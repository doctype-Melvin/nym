import knime.scripting.io as knio
import pdfplumber
import pandas as pd
import re

# --- START --- layout analyzing function --- START ---
# Detect page layout and parse content
def analyze_layout_and_extract(page):

    width = page.width
    words = page.extract_words()
    if not words:
        return ""

    # 1. Create a map of horizontal occupancy
    # mark every x-coordinate that has text
    # 'the hit map'
    occupancy = [0] * int(width)
    for word in words:
        for x in range(int(word['x0']), int(word['x1'])):
            if x < len(occupancy):
                occupancy[x] += 1

    # 2. Find gutters or vertical strip of white space
    min_gutter_width = 13  # Adjust based on average resume spacing
    gaps = []
    current_gap_start = None
    
    for x, count in enumerate(occupancy):
        if count == 0:
            if current_gap_start is None:
                current_gap_start = x
        else:
            if current_gap_start is not None:
                gap_width = x - current_gap_start
                if gap_width >= min_gutter_width:
                    gaps.append((current_gap_start, x))
                current_gap_start = None

    # 3. Determine layout based on gutters
    # ignore gaps that are just page margins
    internal_gutters = [g for g in gaps if g[0] > width * 0.1 and g[1] < width * 0.9]

    if not internal_gutters:
        # Single Column
        return page.extract_text(layout=True)
    
    # 4. Multi-column extraction
    # Sort columns by their horizontal position and extract
    columns = []
    current_x = 0
    
    # Create crops based on gutters
    for g_start, g_end in internal_gutters:
        columns.append(page.crop((current_x, 0, g_start, page.height)).extract_text() or "")
        current_x = g_end
    
    # Add the final column
    columns.append(page.crop((current_x, 0, width, page.height)).extract_text() or "")
    
    return "\n".join(columns)

# --- END --- layout analyzing function --- END ---

# ---- UTILITY FN ----
# Remove all unnecessary whitespace and linebreaks from text
clean_text = lambda t:  ' '.join(t.replace('\n', ' ').split())

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
output = []
all_pii = []
all_text = []
swissed = []

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