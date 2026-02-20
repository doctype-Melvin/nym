import knime.scripting.io as knio
import pandas as pd
import spacy
import json

nlp = spacy.load("de_core_news_lg")

def is_person(token):
    # simple heuristic to check if noun is likely a person
    text = token.text.lower()

    blacklist = {"september", "oktober", "november", "dezember"}
    if text in blacklist:
        return False
    
    if token.ent_type_ in ["DATE", "TIME", "CARDINAL"]:
        return False

    person_suffixes = ( # common German suffixes for job titles
        "er", "in", "ent", "ant", "ist", "ling", "experte", "leiter"
    )

    # sufix check
    if text.endswith(person_suffixes):
        return True
    
    # matches spaCy NER logic?
    if token.ent_type_ == "PER":
        return True
    
    return False

def read_gender(content):
    doc = nlp(content)
    gender_hits = []
    
    for token in doc:
        # target Nouns, Proper Nouns, and Pronouns
        if token.pos_ in ["NOUN", "PROPN", "PRON"]:
            if is_person(token) or token.pos_ == "PRON":
            # Access morphological dict (e.g., {'Gender': 'Fem', 'Number': 'Sing'})
                morph = token.morph.to_dict()
                
                # Check if 'Gender' is present
                if "Gender" in morph:
                    gender_hits.append({
                        "text": token.text,
                        "start": token.idx,
                        "end": token.idx + len(token.text),
                        "gender": morph["Gender"],
                        "pos": token.pos_,
                        "morph": str(token.morph)
                    })
                
    return json.dumps(gender_hits)

# KNIME instructions
input_df = knio.input_tables[0].to_pandas()
results = []

for content in input_df['Redacted']:
    results.append(read_gender(content))

input_df['Gender_Findings'] = results
knio.output_tables[0] = knio.Table.from_pandas(input_df)