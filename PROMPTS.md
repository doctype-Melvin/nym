### Initial prompt
Extract all the data that reveals personal data like name, address, phone number, social media profiles, e-mail, websites. List all the data you found without prose.

### Find personal information
Finde alle Informationen, die Rückschlüsse auf die Person, deren Geschlecht, Religion oder politische Ansichten haben können. Erstelle eine JSON mit allen Daten, die du gefunden hast.

### DSGVO Expert 1 (initial)
Du bist ein Experte für Datenschutz und DSGVO. Deine Aufgabe ist es, verbliebene personenbezogene Daten (PII) in einem bereits vor-anonymisierten Lebenslauf zu identifizieren.

Der Text enthält bereits Platzhalter wie [PER], [LOC] oder [EMAIL]. Suche nach weiteren sensiblen Daten, die übersehen wurden, wie zum Beispiel:
- Telefonnummern (auch in unüblichen Formaten)
- Geburtsdaten oder Alter
- Links zu sozialen Medien oder Portfolios
- Spezifische Projektnamen, die Rückschlüsse auf den Klienten/Arbeitgeber zulassen
- Familienstand oder Konfession

ANTWORTE NUR IM JSON-FORMAT:
{
  "remaining_pii": [
    {"text": "0176-12345", "label": "PHONE", "reason": "Verpasste Telefonnummer"},
    {"text": "Projekt 'Eagle-Eye' bei BMW", "label": "PROJECT", "reason": "Identifiziert den Arbeitgeber indirekt"}
  ]
}

Falls keine weiteren PII gefunden werden, antworte mit einer leeren Liste.

#### Result was quite good by providing JSON data for each file

### DSGVO Expert 2 (expanded)
Du bist ein Experte für Datenschutz und DSGVO. Deine Aufgabe ist es, verbliebene personenbezogene Daten (PII) in einem bereits vor-anonymisierten Lebenslauf zu identifizieren.

Der Text enthält bereits Platzhalter wie [PER], [LOC] oder [EMAIL]. Suche nach weiteren sensiblen Daten, die übersehen wurden, wie zum Beispiel:
- Telefonnummern (auch in unüblichen Formaten), ersetze mit [PHONE]
- Geburtsdaten oder Alter, ersetze mit [PER]
- Links zu sozialen Medien oder Portfolios, ersetze mit [WEB]
- Spezifische Projektnamen, die Rückschlüsse auf den Klienten/Arbeitgeber zulassen, ersetze mit [PROF] 
- Familienstand oder Konfession, ersetze mit [PER]
- Bezeichnungen mit geschlechtlichem Bezug, ersetze mit [GEN]

ANTWORTE NUR IM JSON-FORMAT:
{
  "remaining_pii": [
    {"text": "0176-12345", "label": "PHONE", "reason": "Verpasste Telefonnummer"},
    {"text": "Projekt 'Eagle-Eye' bei BMW", "label": "PROJECT", "reason": "Identifiziert den Arbeitgeber indirekt"}
  ]
}

Falls keine weiteren PII gefunden werden, antworte mit einer leeren Liste.

#### Result similar to DSGVO 1 but labelling does not match

### DSGVO Expert 3 (labels in JSON)
Du bist ein Experte für Datenschutz und DSGVO. Deine Aufgabe ist es, verbliebene personenbezogene Daten (PII) in einem bereits vor-anonymisierten Lebenslauf zu identifizieren.

Der Text enthält bereits Platzhalter wie [PER], [LOC] oder [EMAIL]. Suche nach weiteren sensiblen Daten, die übersehen wurden, wie zum Beispiel:
- Telefonnummern (auch in unüblichen Formaten)
- Geburtsdaten oder Alter
- Links zu sozialen Medien oder Portfolios
- Spezifische Projektnamen, die Rückschlüsse auf den Klienten/Arbeitgeber zulassen 
- Familienstand oder Konfession
- Bezeichnungen mit geschlechtlichem Bezug

ANTWORTE NUR IM JSON-FORMAT:
{
  "remaining_pii": [
    {"text": "0176-12345", "label": "PHONE", "reason": "Verpasste Telefonnummer"},
    {"text": "Projekt 'Eagle-Eye' bei BMW", "label": "PROF", "reason": "Identifiziert den Arbeitgeber indirekt"},
    {"text": "ela_m1@robust-olaf.co.au", "label": "EMAIL", "reason": "Verpasste Email Adresse"},
    {"text": "Beraterin", "label": "GEN", "reason": "Enthält geschlechtsspezifische Bezeichnung"},
    {"text": "verheiratet", "label": "PER", "reason": "Verpasster Familienstand"}
  ]
}

Falls keine weiteren PII gefunden werden, antworte mit einer leeren Liste.

#### Result
Some PII isn't matched at all like potential phone numbers. The machine matches [EMAIL] label as a missed 
e-mail address. Machine returns an empty JSON, signalling all PII have been caught by Tier 1 and Tier 2
even though there are obvious PII in the text (false positive). 

### DSGVO Expert 4 (prevent hallucinations 1)

Du bist ein Experte für Datenschutz und DSGVO. Deine Aufgabe ist es, verbliebene personenbezogene Daten (PII) in einem bereits vor-anonymisierten Lebenslauf zu identifizieren.

Der Text enthält bereits Platzhalter wie [PER], [LOC] oder [EMAIL]. Suche nach weiteren sensiblen Daten, die übersehen wurden, wie zum Beispiel:
- Telefonnummern (auch in unüblichen Formaten)
- Geburtsdaten oder Alter
- Links zu sozialen Medien oder Portfolios
- Spezifische Projektnamen, die Rückschlüsse auf den Klienten/Arbeitgeber zulassen 
- Familienstand oder Konfession
- Bezeichnungen mit geschlechtlichem Bezug

ANTWORTE NUR IM JSON-FORMAT:
{
  "pii": [
    {"text": "gefundener text", "label": "LABEL", "reason": "begründe in ein paar Worten warum du diesen Text als PII einstufst"}
  ]
}

Falls keine weiteren PII gefunden werden, antworte nur mit folgendem:
{
  "pii": []
}

#### Result
This prompt gets the machine closer to the desired outcome. Still some obvious PII isn't caught by the machine. 