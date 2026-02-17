import re

def to_titlecase(text):

    def replace_match(match):
        word = match.group(0)
        return word.title() if len(word) >= 4 else word
    return re.sub(r'\b[A-ZÜÖÄß]{3,}\b', replace_match, text)