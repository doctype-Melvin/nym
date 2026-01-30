# This script creates separate Tier 1 (regex)
# and Tier 2 (spaCy) layers and replaces detected
# PII with masking strings of the same length of PII

import knime.scripting.io as knio
import pdfplumber
import pandas as pd
import spacy
import re


nlp = spacy.load("de_core_news_lg")

# Describe REGEX patterns
patterns = [
    {"label": "EMAIL",
    "pattern": [{"TEXT": {"REGEX": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"}}]},
    {"label": "PHON1",
    "pattern": [{"TEXT": {"REGEX": r"(?:\+49|0049|0)(?:\s?\d{2,5})(?:\s?\d{4,10})"}}]},
    {"label": "PHON2",
    "pattern": [{"TEXT": {"REGEX": r"(?:\+49|0)[-/\s.]?\d{2,5}[-/\s.]?\d{4,10}"}}]},
    {"label": "PHON3",
    "pattern": [{"TEXT": {"REGEX": r"(?:\+49|0)\s?\(0\)\s?\d{2,5}\s?\d{4,10}"}}]},
    {"label": "SOCI",
    "pattern": [{"TEXT": {"REGEX": r"@[a-zA-Z0-9_]{2,30}(?=$| )"}}]},
    {"label": "WEB",
    "pattern": [{"TEXT": {"REGEX": r"\b(?<!mailto:)(?<!@)(?:https?:\/\/)?(?:www\.)?(?!\d)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:\/[^\s<>\"'@]*|(?!\S))?\b(?![\w@./])"}}]},
]


tier1_regex = [
    {
        "label": "EMAIL",
        "pattern": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    },
    {
        "label": "PHONE_DE",
        "pattern": r"(?:(?:\+?49[ \-\.\(\)]?)?(?:(?:\(?0\d{1,5}\)?)|(?:\d{1,5}))[ \-\.\(\)]?(?:\d[ \-\.\(\)]?){5,10}\d)"
    },
    {
        "label": "WEB",
        "pattern": r"\b(?<!mailto:)(?<!@)(?:https?:\/\/)?(?:www\.)?(?!\d)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:\/[^\s<>\"'@]*|(?!\S))?\b(?![\w@./])"
    },
    {
        "label": "SOCI",
        "pattern": r"@[A-Za-z0-9](?:[A-Za-z0-9._-]{1,28}[A-Za-z0-9])?"
    }

]

ent_labels = ["PER", "LOC", 'PHONE', 'EMAIL']

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

# --- START --- entity masking function --- START ---
def mask_entities(doc):
    # Sort entities by start character index (reverse)
    ents = sorted(doc.ents, key=lambda e: e.start_char, reverse=True)
    text = doc.text
    for ent in ents:
        if ent.label_ in ent_labels:
            # Replace the exact character slice spaCy found
            #text = text[:ent.start_char] + f"[{ent.label_}]" + text[ent.end_char:]
            text = text[:ent.start_char] + "***" + text[ent.end_char:]

    return text
# --- END --- entity masking function --- END ---

# --- START --- TIER 1 masking layer --- START ---
def apply_tier1(text):
    all_matches = []
    # for each rule in list
    for rule in tier1_regex:
        # find matches for the current pattern
        for match in re.finditer(rule["pattern"], text):
            # print(match.start(), match.end(), rule["label"])
            all_matches.append({
                "start": match.start(),
                "end": match.end(), 
                "label": rule["label"],
                "length": match.end() - match.start()
                })
                
    
    # Sort ascending and rule to let the longest win
    all_matches.sort( key=lambda m: (m["start"], -m["length"]))

    # collision resolver greedy
    result = []
    last_end = -1

    for m in all_matches:
        if m["start"] >= last_end:
            result.append(m)
            last_end = m["end"]

    # Sort reverse to prevent character offset while cutting
    result.sort( key=lambda m: m["start"], reverse=True)

    # mask matches in text
    for m in result:
        text = text[:m["start"]] + f'[{m["label"]}]' + text[m["end"]:]
        #print(text)
    return text
    

# ---- UTILITY FN ----
# Remove all unnecessary whitespace and linebreaks from text
clean_text = lambda t:  ' '.join(t.replace('\n', ' ').split())

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
whole_content = []
all_pii = []
all_text = []
swissed = []
tier1 = []

# Loop over all provided filepaths in dir
for path in input_df['Filepath']:
    if not str(path).lower().endswith('.pdf'):
        whole_content.append(f"SKIPPED: not a PDF {path}")
        all_pii.append("SKIPPED: not a PDF")
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

    # TIER 1 - Apply tier 1 detection
    tier1.append(apply_tier1(full_content))

    # Feed the content to spaCy (language model) to match entities
    content = nlp(full_content)
        
    # Create swissed version of content
    swissed.append(mask_entities(content))

    # List of found entity text and entity label
    # clean_text is a utility function and removes whitespace
    list_text_and_label = [f"{clean_text(ent.text)} ({ent.label_})" for ent in content.ents if ent.label_ in ent_labels]

    # list of found entity text 
    list_text =  [f"{clean_text(ent.text)}" for ent in content.ents if ent.label_ in ent_labels]
        
    whole_content.append(full_content)
    all_pii.append(", ".join(list_text_and_label))
    all_text.append(", ".join(list_text))

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_df['Filepath'],
    "Content": whole_content,
    "Tier1": tier1
    #"Text and Label": all_pii,
    #"Text": all_text,
    #"To LLM": swissed
    }))