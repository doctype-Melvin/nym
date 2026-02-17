import re
import spacy
import json
import pandas as pd
import sqlite3
from collections import defaultdict
from datetime import datetime


# CONFIG & MODEL LOADING
# spaCy
try:
    nlp = spacy.load("de_core_news_lg")
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        patterns = [
            {"label": "LOC_STR1", "pattern": [{"TEXT": {"REGEX": r"(?i).+(straße|str\.|weg|platz|allee|gasse|damm)$"}}]},
            {"label": "LOC_STR2", "pattern": [{"TEXT": {"REGEX": r"(?i).+(straße|str\.|weg|platz)$"}}, {"IS_DIGIT": True}]}
        ]
        ruler.add_patterns(patterns)
except Exception as e:
    print(f"Error loading spaCy: {e}")

# titlecasing utility fn
def to_titlecase(text):
    def replace_match(match):
        word = match.group(0)
        return word.title() if len(word) >= 4 else word
    return re.sub(r'\b[A-ZÜÖÄß]{3,}\b', replace_match, text)

# Custom Regex
TIER1_PATTERNS = [
    {"label": "EMAIL", "pattern": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"},
    {"label": "PHONE_DE", "pattern": r"(?:(?:\+?49[ \-\.\(\)]?)?(?:(?:\(?0\d{1,5}\)?)|(?:\d{1,5}))[ \-\.\(\)]?(?:\d[ \-\.\(\)]?){5,10}\d)"},
    {"label": "WEB", "pattern": r"\b(?<!mailto:)(?<!@)(?:https?:\/\/)?(?:www\.)?(?!\d)([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:\/[^\s<>\"'@]*|(?!\S))?\b(?![\w@./])"},
    {"label": "SOCI", "pattern": r"@[A-Za-z0-9](?:[A-Za-z0-9._-]{1,28}[A-Za-z0-9])?"},
    {"label": "LOC", "pattern": r"\b\d{5}\b"},
    {"label": "DATE", "pattern": r"\b\d{1,2}\.\d{1,2}\.(\d{4}|\d{2})\b"},
    {"label": "DATE", "pattern": r"(?i)\b\d{1,2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s\d{4}\b"},
    {"label": "DATE", "pattern": r"(?i)\b\d{2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s\d{4}\b"},
    {"label": "DATE", "pattern": r"(?i)\b\d{1,2}\.\s(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s'\d{2}\b"}
]

# CORE FUNCTIONS

def get_beam_confidence(doc, beam_width=16, beam_density=0.0001):
    ner = nlp.get_pipe("ner")
    beams = ner.beam_parse([doc], beam_width=beam_width, beam_density=beam_density)
    entity_scores = defaultdict(float)
    for beam in beams:
        for score, ents in ner.moves.get_beam_parses(beam):
            for start, end, label in ents:
                entity_scores[(start, end, label)] += score
    return entity_scores

def run_pii_detection(text, manual_overrides=None):
    """Combines Tier 1 and Tier 2 Detection logic"""
    all_hits = []
    
    # Tier 1: Regex
    for rule in TIER1_PATTERNS:
        for match in re.finditer(rule["pattern"], text):
            all_hits.append({
                "start": match.start(), "end": match.end(),
                "label": rule["label"], "source": "Tier 1",
                "length": match.end() - match.start()
            })
            
    # Manual Search & Tag Overrides
    if manual_overrides:
        for phrase, label in manual_overrides.items():
            for match in re.finditer(re.escape(phrase), text):
                all_hits.append({
                    "start": match.start(), "end": match.end(),
                    "label": label, "source": "Manual",
                    "length": len(phrase)
                })

    # Tier 2: spaCy
    doc = nlp(text)
    beam_scores = get_beam_confidence(doc)
    ent_labels = ["PER", "LOC", 'PHONE', 'EMAIL']
    
    for ent in doc.ents:
        if ent.label_ in ent_labels or ent.label_.startswith("LOC_STR"):
            score_key = (ent.start, ent.end, ent.label_)
            conf = 1.0 if (ent.ent_id or "STR" in ent.label_) else beam_scores.get(score_key, 0.0)
            all_hits.append({
                "start": ent.start_char, "end": ent.end_char,
                "label": ent.label_, "source": "Tier 2",
                "length": ent.end_char - ent.start_char,
                "confidence": round(float(conf), 3)
            })

    # Conflict Resolution (The Merger logic)
    all_hits.sort(key=lambda x: (x['start'], -x['length']))
    final_hits = []
    last_end = -1
    for h in all_hits:
        if h['start'] >= last_end:
            final_hits.append(h)
            last_end = h['end']
            
    return final_hits

def apply_neutralizer(text, job_dict_df):
    """Tier 3: Neutralization Logic"""
    current = text
    # 1. Pattern Neutralization
    kauf_patterns = [
        (r"\b(\w+)(kaufmann|kauffrau)\b", r"\1fachkraft"),
        (r"\b(Kaufmann|Kauffrau)\s+für\b", "Fachkraft für"),
        (r"\b(Kaufmann|Kauffrau)\s\b", "Fachkraft ")
    ]
    for pattern, replacement in kauf_patterns:
        current = re.sub(pattern, replacement, current, flags=re.IGNORECASE)

    # 2. Dictionary Neutralization
    if job_dict_df is not None:
        for _, row in job_dict_df.iterrows():
            target = rf'\b{re.escape(str(row["original"]))}\b'
            current = re.sub(target, row["neutral"], current, flags=re.IGNORECASE)
            
    return current

# --- THE MASTER ORCHESTRATOR ---

def process_complyable(raw_text, db_path="complyable_vault.db", manual_rules=None):
    """The function the UI will call live"""
    # 1. Pre-process
    clean_text = to_titlecase(raw_text)
    
    # 2. Detect PII
    hits = run_pii_detection(clean_text, manual_rules)
    
    # 3. Apply Redaction (Back-to-front)
    hits_sorted = sorted(hits, key=lambda x: x['start'], reverse=True)
    redacted_text = clean_text
    for h in hits_sorted:
        redacted_text = redacted_text[:h['start']] + f"[{h['label']}]" + redacted_text[h['end']:]
        
    # 4. Neutralize
    # Get dict from DB (In a real app, you might cache this for speed)
    try:
        conn = sqlite3.connect(db_path)
        job_df = pd.read_sql_query("SELECT original, neutral FROM job_dict", conn)
        conn.close()
    except:
        job_df = None
        
    final_output = apply_neutralizer(redacted_text, job_df)
    
    return final_output, hits