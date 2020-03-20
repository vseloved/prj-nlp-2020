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
            # print(text_to_search)
        else:
            is_hyphened = False
            replaced_text += text_to_search
    
    return replaced_text

def format_headline(text):
    doc = nlp(text)

    prepared_tokens = []
    
    #print("?????", doc)
    for token in doc:
        if token.whitespace_:
            #print("LEN", len(token.text), token)
            token_text = token.text_with_ws.capitalize() if len(token.text) > 3 else token.text_with_ws
        else:
            #print("LEN", len(token.text), token)
            token_text = token.text.capitalize() if len(token.text) > 3 else token.text
        
        if token.pos_ in ['NOUN', 'PROPN', "PRON", "ADJ", "ADV"]:
            #print('POS', token)
            token_text = token_text.capitalize()
        elif token.pos_ == "SCONJ" and token.dep_ != "prep":
            #print('POS', token)
            token_text = token_text.capitalize()
        elif token.pos_ == "DET" and token.tag_ == "PRP$":
            token_text = token_text.capitalize()
        elif token.pos_ == "VERB" or token.tag_ in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            token_text = token_text.capitalize()
        # if token.text == "-":
        #     print(token.doc)
        #     print(token.sent)
            


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

    #print("######", "".join(prepared_tokens))
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
        else:
            print(len(format_headline(raw)), len(pure))
            print(format_headline(raw))
            print(pure)


    print(f'{correct_count}/{len(data)}')


