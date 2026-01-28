import knime.scripting.io as knio
import pdfplumber
import pandas as pd
import spacy
from spacy.tokens import Span
from spacy.util import filter_spans
import re
from spacy.pipeline import EntityRuler

nlp = spacy.load("de_core_news_lg")

# --- modify entity ruler ---
# 1. Add EntityRuler before "ner" step
# Add rules before the content is passed to spaCy
if "entity_ruler" not in nlp.pipe_names:
    ruler = nlp.add_pipe("entity_ruler", before="ner")

# 2. Describe REGEX patterns
patterns = [
    {"label": "EMAIL",
    "pattern": [{"TEXT": {"REGEX": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"}}]},
    {"label": "PHONE",
    "pattern": [{"TEXT": {"REGEX": r"(?:\+49|0049|0)(?:\s?\d){7,15}"}}]},
    {"label": "SOCI",
    "pattern": [{"TEXT": {"REGEX": r"@[a-zA-Z0-9_]{2,30}(?=$| )"}}]},
    {"label": "WEB",
    "pattern": [{"TEXT": {"REGEX": r"\b(?<!mailto:)(?<!@)(?:https?:\/\/)?(?:www\.)?(?!\d)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:\/[^\s<>\"'@]*|(?!\S))?\b(?![\w@./])"}}]},
]

ruler.add_patterns(patterns)

ent_labels = ["PER", "LOC", 'PHONE', 'EMAIL', 'SOCI', 'WEB']

# --- layout analyzing function START ---
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


# --- layout analyzing function END ---

#print("- Notation - ", patterns[0]['pattern'][0]['TEXT']['REGEX'])
# go through the patterns list programmatically and find the 

# --- regex function START ---
# Catch PII with regex
# this fn is related to the confidence scoring
# could be abandoned for a different approach
def regex_pii_matcher(text):
    phone_pattern = r"(?:\+49|0049|0)(?:\s?\d){7,15}"
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    matches = []
    for phone in re.finditer(phone_pattern, text):
        matches.append((phone.start(), phone.end(), 'PHONE'))
    for mail in re.finditer(email_pattern, text):
        matches.append((mail.start(), mail.end(), 'EMAIL'))
    return matches

# --- regex function END ---

# -------------------------------------------------------------------------------

#----- UTILS ---------------------------------
# Remove all unnecessary whitespace and linebreaks from text
clean_text = lambda t:  ' '.join(t.replace('\n', ' ').split())


# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
whole_content = []
all_pii = []
re_count = []

for path in input_df['Filepath']:
    if not str(path).lower().endswith('.pdf'):
        whole_content.append(f"SKIPPED: not a PDF {path}")
        all_pii.append("SKIPPED: not a PDF")
        continue

    full_resume_text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = analyze_layout_and_extract(page)
            #full_resume_text.append(re.sub(r'\n\s*\n', '\n', page_text))
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

    # Feed the content to the language model
    # --- Here the actual content is passed to spaCy ---
    # spaCy extracts the matched entities
    content = nlp(full_content)

    # Tier 1 PII identification
    # Regex matching
    regex_hits = regex_pii_matcher(full_content)

    # Adding regex results to spaCy as Spans
    # 1. Create a list of found entities
    regex_ents = []
    for start, end, label in regex_hits:
        span = content.char_span(start, end, label=label, alignment_mode='contract')
        if span is not None:
            regex_ents.append(span)

    # 2. Append regex hits to original entity list
    content.ents = filter_spans(list(content.ents) + regex_ents)
    
    # iterating over the regex_ents list shows all regex matches with
    # their corresponding label
    #for ent in regex_ents:
    #    print(f"{ent.text} ({ent.label_})")

    # Scan content for entities and add them to the pii list
    scan_pii = [f"{clean_text(ent.text)} ({ent.label_})" for ent in content.ents if ent.label_ in ent_labels]

    # list of pii string
    list_pii =  [f"{clean_text(ent.text)}" for ent in content.ents if ent.label_ in ent_labels]
        
    whole_content.append(full_content)
    all_pii.append(", ".join(scan_pii))
    re_count.append(len(regex_hits))

knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_df['Filepath'],
    "Content": whole_content,
    "PII hits": all_pii,
    "regex count": re_count
    }))