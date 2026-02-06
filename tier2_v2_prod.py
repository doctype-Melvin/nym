import knime.scripting.io as knio
import pandas as pd
import spacy
import re
import json
from collections import defaultdict

nlp = spacy.load("de_core_news_lg")

ruler = nlp.add_pipe("entity_ruler", before="ner")
patterns = [
    # Catches Dorfstraße, Dorfstr., Dorf str, etc.
    {"label": "LOC_STR1", "pattern": [{"TEXT": {"REGEX": r"(?i).+(straße|str\.|weg|platz|allee|gasse|damm)$"}}]},
    # Catches house numbers following the street
    {"label": "LOC_STR2", "pattern": [{"TEXT": {"REGEX": r"(?i).+(straße|str\.|weg|platz)$"}}, {"IS_DIGIT": True}]}
]
ruler.add_patterns(patterns)

ent_labels = ["PER", "LOC", 'PHONE', 'EMAIL']

# Remove all unnecessary whitespace and linebreaks from text
clean_text = lambda t:  ' '.join(t.replace('\n', ' ').split())

# --- START --- TIER 2 --- START ---
def get_tier2(doc, nlp, filename):
    all_matches = []
    new_logs = []

    beam_scores = get_beam_confidence(nlp, doc)
    # for each rule in list
    for ent in doc.ents:
        if ent.label_ in ent_labels:

            score_key = (ent.start, ent.end, ent.label_)

            if ent.ent_id or ent.label_ in ['LOC_STR1', 'LOC_STR2']:
                conf = 1.0
            else:
                conf = beam_scores.get(score_key, 0.0)

            conf = round(float(conf), 4)

            all_matches.append({
                "start": ent.start_char,
                "end": ent.end_char, 
                "label": ent.label_,
                "length": ent.end_char - ent.start_char,
                "confidence": conf
                })
            new_logs.append({
                'File': filename,
                'Node': 'Tier 2 spaCy DEU',
                'Action': 'Redact',
                'Detail': f'PII found: ({ent.label_})',
                'Start': ent.start_char,
                'End': ent.end_char,
                'Score': conf
                })
        

    return all_matches, new_logs
# --- END --- Tier2 --- END ----

# --- START - BEAM SEARCH CONF - START ---
def get_beam_confidence(nlp, doc, beam_width=16, beam_density=0.0001):
    ner = nlp.get_pipe("ner")
    
    #Run the beam parser (This explores 16 alternative interpretations)
    beams = ner.beam_parse([doc], beam_width=beam_width, beam_density=beam_density)
    
    entity_scores = defaultdict(float)
    
    for beam in beams:
        for score, ents in ner.moves.get_beam_parses(beam):
            for start, end, label in ents:
                # Store the probability of this specific start/end/label combo
                entity_scores[(start, end, label)] += score
                
    return entity_scores

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()

tier2_out = []
all_logs = []

try: 
    cumulative_log = knio.input_tables[1].to_pandas().to_dict('records')
except:
    cumulative_log = []

# Loop over all provided filepaths in dir
for content, filepath in zip(input_df['Content'], input_df['Filepath']):

    doc = nlp(content)

    all_matches, new_logs = get_tier2(doc, nlp, filepath)

    for log in new_logs:
        cumulative_log.append({
            'Timestamp': pd.Timestamp.now().strftime('%d.%m.%Y %H:%M:%S'),
            'Filepath': filepath,
            'Event_type': 'PII_Detection_T2',
            'Description': log['Detail'],
            'Start': log['Start'],
            'End': log['End'],
            'Confidence_Score': log['Score'],
            'Details': "NLP matching using spaCy library - model: de_core_news_lg"
        })

    tier2_out.append(json.dumps(all_matches))

output_df = input_df.copy()
output_df['Tier2_matches'] = tier2_out

cumulative_log = pd.DataFrame(cumulative_log)

knio.output_tables[0] = knio.Table.from_pandas(output_df)
knio.output_tables[1] = knio.Table.from_pandas(cumulative_log)