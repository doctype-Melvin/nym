import re
import spacy
import json
import pandas as pd
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "vault" / "complyable_vault.db"

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
    text = re.sub(r'(?<=[A-Z])\s(?=[A-Z])', '', text) 
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

#Part of Neutralizer logic to detect person-related tokens

def is_person_related(token):
    """
    Heuristic to filter nouns to person-related/job titles only.
    Essential for reducing 'Highlight Fatigue' in the UI.
    """
    text = token.text.lower()
    
    # 1. HARD BLACKLIST (Months & High-Frequency False Positives)
    # These often pass the '-er' suffix check but are never people.
    blacklist = {
        "september", "oktober", "november", "dezember", 
        "zimmer", "nummer", "uhr", "meter", "liter", "wasser", "fehler"
    }
    if text in blacklist:
        return False

    # 2. SEMANTIC CHECK (Leverage spaCy's pre-built Entity Recognition)
    # If the NER engine already tagged this as a Date, Time, or Quantity, ignore it.
    if token.ent_type_ in ["DATE", "TIME", "CARDINAL", "QUANTITY"]:
        return False

    # 3. SUFFIX SIEVE (The core of German person-noun detection)
    person_suffixes = (
        "er", "in", "ent", "ant", "ist", "kraft", 
        "experte", "leiter", "coach", "berater", "führung"
    )
    if text.endswith(person_suffixes):
        return True
    
    # 4. EXPLICIT PERSON CHECK
    # If spaCy identifies the word as a Person (PER), we want it.
    if token.ent_type_ == "PER":
        return True
        
    return False

def apply_neutralizer(text, filepath, job_dict_df=None):
    """
    Tier 3: Hybrid Neutralizer (Regex + Dict + Linguistic Sensor)
    Returns: (processed_text, list_of_events)
    """
    events = []
    current = str(text)
    ts_format = '%d.%m.%Y %H:%M:%S'
    
    # 1. THE ACTUATOR: Regex Patterns (High Confidence)
    kauf_patterns = [
        (r"\b(\w+)(kaufmann|kauffrau)\b", r"\1fachkraft", "Group Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s+für\b", "Fachkraft für", "Title Neutralization"),
        (r"\b(Kaufmann|Kauffrau)\s\b", "Fachkraft ", "Title Neutralization")
    ]

    for pattern, replacement, label in kauf_patterns:
        matches = re.finditer(pattern, current, flags=re.IGNORECASE)
        for m in matches:
            events.append({
                'Timestamp': datetime.now().strftime(ts_format),
                'Filepath': filepath,
                'Event_type': 'Neutralization',
                'Description': f"Pattern: '{m.group(0)}' -> '{replacement}'",
                'Start': m.start(),
                'End': m.end(),
                'Confidence_Score': 1.0,
                'Details': f"Regex-Rule: {label}"
            })
        current = re.sub(pattern, replacement, current, flags=re.IGNORECASE)

    # 2. THE ACTUATOR: Dictionary Lookup (User Approved)
    if job_dict_df is not None:
        # Sort dict by length descending to prevent substring issues
        sorted_dict = job_dict_df.iloc[job_dict_df['original'].str.len().argsort()[::-1]]
        for _, row in sorted_dict.iterrows():
            target = rf'\b{re.escape(str(row["original"]))}\b'
            if re.search(target, current, flags=re.IGNORECASE):
                # For simplicity in the log, we mark start/end as context-based
                events.append({
                    'Timestamp': datetime.now().strftime(ts_format),
                    'Filepath': filepath,
                    'Event_type': 'Neutralization',
                    'Description': f"Dict: '{row['original']}' -> '{row['neutral']}'",
                    'Start': 0, 'End': 0, # Global replace
                    'Confidence_Score': 0.95,
                    'Details': 'Manual Dictionary Match' 
                })
                current = re.sub(target, row["neutral"], current, flags=re.IGNORECASE)

    # 3. THE SENSOR: Linguistic Detection (spaCy Morphology)
    # We run this AFTER replacements to catch only what remains
    doc = nlp(current)
    for token in doc:
        if (token.pos_ in ["NOUN", "PROPN", "PRON"]) and (is_person_related(token) or token.pos_ == "PRON"):
            morph = token.morph.to_dict()
            if "Gender" in morph:
                # We do NOT replace here, we only flag for the UI/Audit Log
                events.append({
                    'Timestamp': datetime.now().strftime(ts_format),
                    'Filepath': filepath,
                    'Event_type': 'Compliance_Flag',
                    'Description': f"Detected gendered term '{token.text}'",
                    'Start': token.idx,
                    'End': token.idx + len(token.text),
                    'Confidence_Score': 0.75,
                    'Details': f"Morphology ({morph['Gender']}): Flagged for human review"
                })
    
    return current, events

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