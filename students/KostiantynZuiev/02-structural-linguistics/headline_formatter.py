import json
import spacy

nlp = spacy.load('en_core_web_md')

def format_headline(text):
    doc = nlp(text)

    prepared_tokens = []
    for token in doc:
        if token.whitespace_:
            token_text = token.text_with_ws.capitalize() if len(token.text) > 3 else token.text_with_ws
        else:
            token_text = token.text.capitalize() if len(token.text) > 3 else token.text
        prepared_tokens.append(token_text)

    return "".join(prepared_tokens)


with open('data/headlines-test-set.json', 'r') as f: 
    data = json.loads(f.read()) 

    

