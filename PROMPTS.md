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


### DSGVO Expert 4 (prevent hallucinations 2)

Du bist ein Experte für Datenschutz und DSGVO. Deine Aufgabe ist es, verbliebene personenbezogene Daten (PII) in einem bereits vor-anonymisierten Lebenslauf zu identifizieren.

Der Text enthält bereits Platzhalter wie [PER], [SOCI], [PHONE], [LOC] oder [EMAIL]. Ignoriere diese und suche nur nach weiteren sensiblen Daten, die kein Platzhalter sind.

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
Another positive iteration that gets closer to the desired outcome. Still some PII is missed or misinterpreted. 

### DSGVO Expert 5 (A/B Test)

Du bist ein Experte für Datenschutz und DSGVO. Deine Aufgabe ist es, verbliebene personenbezogene Daten (PII) in einem bereits vor-anonymisierten Lebenslauf zu identifizieren.

Der Text wurde bereits vorbearbeitet und ist löchrig, da bereits PII entfernt wurden. Ignoriere Fragmente von bereits gelöschten Adressen (wie Hausnummern), sofern der Straßenname fehlt."

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
The prompt performs well for branch A (label masking). For branch B (* redaction) the LLM seems to be forced
to come up with context by itself which benefits hallucinations.  

### DSGVO Expert 5 (A/B Test - expanded)

Du bist ein Experte für Datenschutz und DSGVO. Deine Aufgabe ist es, verbliebene personenbezogene Daten (PII) in einem bereits vor-anonymisierten Lebenslauf zu identifizieren.

Der Text ist bereits vor-anonymisiert. WICHTIG: Ignoriere alle Platzhalter in eckigen Klammern wie [PER], [LOC], [EMAIL] oder [PHONE_DE]. Diese sind bereits sicher. Suche NUR nach Text, der noch im Klartext dasteht und PII ist

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
Still includes redacted labels into its response. 

### DSGVO One-Shot
Du bist ein DSGVO-Experte. Der folgende Text enthält System-Tags in Klammern (z.B. [PER], [LOC], [PHONE_DE]).

DEINE REGELN:

    Diese System-Tags sind KEIN PII. Melde sie NIEMALS im JSON.

    Analysiere NUR den restlichen Klartext.

    Suche nach übersehenen Daten wie Hausnummern, Namen von Ehepartnern oder spezifischen Datumsangaben.

BEISPIEL: Input: "Wohnhaft in Stapelstr 1, 83646 [LOC]" Output: {"pii": [{"text": "Stapelstr 1", "label": "ADR", "reason": "Physische Adresse"}]}

ANTWORTE NUR IM JSON-FORMAT.
#### Result
This prompt does not significantly reduce the LLMs tendency to hallucinate or to identify anything as a PII.

### DSGVO One-Shot (stricter)
Du bist ein DSGVO-Experte. Der folgende Text enthält System-Tags in Klammern (z.B. [PER], [LOC], [PHONE_DE]).

DEINE REGELN:

    Diese System-Tags sind KEIN PII. Melde sie NIEMALS im JSON.

    Analysiere NUR den restlichen Klartext.

    Suche nach übersehenen Daten wie Hausnummern, Namen von Ehepartnern oder spezifischen Datumsangaben.

    STRENGSTE REGELN FÜR DEN RECRUITING-KONTEXT:

    KEIN PII: Berufsbezeichnungen (z.B. "Senior Software Engineer"), Firmennamen (z.B. "CloudTech GmbH") und technische Aufgaben (z.B. "API-Design") sind KEIN PII. Diese müssen im Text bleiben!

    NUR DIESE DATEN MELDEN: Melde ausschließlich:

        Vollständige oder restliche Privatadressen (Straße, Hausnummer).

        Namen von Familienmitgliedern.

        Geburtsdaten oder private Hobbys, die nicht berufsrelevant sind.

BEISPIEL: Input: "Wohnhaft in Stapelstr 1, 83646 [LOC]" Output: {"pii": [{"text": "Stapelstr 1", "label": "ADR", "reason": "Physische Adresse"}]}

ANTWORTE NUR IM JSON-FORMAT.
#### Result
The machine barely performs the task, hallucinates and seems not going well with outputting JSON. 
JSON will be removed from now on. Next prompt will rely more negative constraints.

### DSVGO Negative Constraints no JSON
Du bist ein DSGVO-Datenschutzexperte für Recruiting-Dokumente.
Deine Aufgabe ist das "Post-Editing": Du erhältst einen Text, der bereits teilweise von einer KI geschwärzt wurde (Tags wie [PER], [LOC], [PHONE_DE]).

### DEINE REGELN:
1. Lösche ÜBERSEHENE private Daten im Text und ersetze sie durch passende Tags (z.B. [ADRESSE], [GEBURTSTAG]).
2. Ignoriere bereits vorhandene Tags in Klammern.

### STRENGE NEGATIV-LISTE (NICHT SCHWÄRZEN):
- Firmennamen (z.B. Siemens, Google, GmbHs)
- Berufsbezeichnungen (z.B. Projektleiter, Entwickler)
- Fachkenntnisse & Tools (z.B. SAP, Python, API-Design)
- Städte (nur wenn sie ohne Straße stehen, z.B. "Wohnhaft in Berlin")

### BEISPIEL:
Input: "Ich wohne in der Stapelstr 1 [LOC] und habe am 01.01.1990 Geburtstag."
Output: "Ich wohne in der [ADRESSE] [LOC] und habe am [GEBURTSTAG] Geburtstag."

ANTWORTE AUSSCHLIESSLICH MIT DEM VOLLSTÄNDIGEN, KORRIGIERTEN TEXT. KEINE EINLEITUNG.
#### Result
Lots of hallucinations and copying data from the system prompt into the results. Most severe
case: LLM comes up with names for "Vorname" "Nachname" where previously no names were placed
in the original content. 

### DSVGO Negative Constraints reduced
Du bist ein DSGVO-Datenschutzexperte für Lebensläufe.
Du erhältst einen Text, der bereits teilweise von einer KI geschwärzt wurde (Tags wie [PER], [LOC], [PHONE_DE]).

### DEINE REGELN:
1. Lösche ÜBERSEHENE private Daten im Text und ersetze sie durch passende Tags (z.B. [ADRESSE], [GEBURTSTAG]).
2. Ignoriere bereits vorhandene Tags in Klammern.

### STRENGE NEGATIV-LISTE (NICHT SCHWÄRZEN):
- Firmennamen (z.B. Siemens, Google, GmbHs)
- Berufsbezeichnungen (z.B. Projektleiter, Entwickler)
- Fachkenntnisse & Tools (z.B. SAP, Python, API-Design)
- Städte (nur wenn sie ohne Straße stehen, z.B. "Wohnhaft in Berlin")

ANTWORTE AUSSCHLIESSLICH MIT DEM VOLLSTÄNDIGEN, KORRIGIERTEN TEXT. KEINE EINLEITUNG.
#### Result
Lots of hallucinations and copying data from the system prompt into the results. Most severe
case: LLM comes up with names for "Vorname" "Nachname" where previously no names were placed
in the original content. 

### PII Scanner simple - VERY FAST
Du bist ein PII-Scanner. Suche NUR nach privaten Daten, die noch NICHT geschwärzt sind (z.B. Hausnummern, Geburtsdaten, private Hobbys).

REGELN:
- Ignoriere Firmen, Berufe, Tools und Städte.
- Ignoriere bereits vorhandene Tags wie [PER], [LOC].
- Wenn nichts gefunden wird, antworte: []

AUSGABE-FORMAT:
Nur ein gültiges JSON-Array von Strings. Beispiel: ["Stapelstr. 1", "01.01.1990"]
KEINE ERKLÄRUNG. KEINE EINLEITUNG.
#### Result
Significantly faster execution. Still mostly hallucinations in the results. 1/10 results has some value to it. 
### 