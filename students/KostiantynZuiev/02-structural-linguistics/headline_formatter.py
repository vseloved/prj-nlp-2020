import json
import spacy
import re
import string

nlp = spacy.load('en_core_web_md')

def fix_hyphen(text):
    is_hyphened = True
    replaced_text = ''
    text_to_search = text
    start_index = 0
    while is_hyphened:
        r = re.search(r'[a-zA-Z0-9]+?(\-[a-zA-Z0-9]+)+', text_to_search)
        if r:
            text_to_replace = r.group(0)
            items = text_to_replace.split("-")
            replacement = "-".join([i.capitalize() for i in items])
            replaced_text += f'{text_to_search[start_index:r.span()[0]]}{replacement}'
            start_index = r.span()[1]
            text_to_search = text_to_search[start_index:]
        else:
            is_hyphened = False
            replaced_text += text_to_search
    
    return replaced_text

def format_headline(text):
    doc = nlp(text)

    prepared_tokens = []

    for token in doc:
        if token.whitespace_:
            token_text = token.text_with_ws.capitalize() if len(token.text) > 3 else token.text_with_ws
        else:
            token_text = token.text.capitalize() if len(token.text) > 3 else token.text
        
        if token.pos_ in ['NOUN', 'PROPN', "PRON", "ADJ", "ADV"]:
            token_text = token_text.capitalize()
        elif token.pos_ == "SCONJ" and token.dep_ != "prep":
            token_text = token_text.capitalize()
        elif token.pos_ == "DET" and token.tag_ == "PRP$":
            token_text = token_text.capitalize()
        elif token.pos_ == "VERB" or token.tag_ in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            token_text = token_text.capitalize()

        prepared_tokens.append(token_text)

    for i, token in enumerate(prepared_tokens):
        if token not in string.punctuation:
            prepared_tokens[i] = token.capitalize()
            break
        else:
            continue
    for i in range(len(prepared_tokens)-1, -1, -1):
        if prepared_tokens[i] not in string.punctuation:
            prepared_tokens[i] = prepared_tokens[i].capitalize()
            break
        else:
            continue

    prepared_text = "".join(prepared_tokens)

    prepared_text = fix_hyphen(prepared_text)

    return prepared_text


if __name__ == "__main__":
    with open('data/headlines-test-set.json', 'r') as f: 
        data = json.loads(f.read()) 

        correct_count = 0
        for raw, pure in data:
            if format_headline(raw) == pure:
                correct_count += 1

        headline_test_set_result = f'Test set result: {correct_count}/{len(data)}'
    with open('data/examiner-headlines.txt', 'r') as f:
        correct_count = 0
        processed_count = 0
        for line in f:
            if line == format_headline(line):
                correct_count += 1
            processed_count += 1
        
        examiner_headlines_result = f'Examiner headlines result: {correct_count}/{processed_count}'
    with open('headlines_results.txt','w') as res_file:
        res_file.write(headline_test_set_result)
        res_file.write('\n')
        res_file.write(examiner_headlines_result)



