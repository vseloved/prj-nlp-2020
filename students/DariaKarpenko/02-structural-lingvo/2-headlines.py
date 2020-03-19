import json
import spacy
nlp = spacy.load("en_core_web_md", disable=['textcat', 'ner'])


def is_notional_pos(token):
    
    if token.tag_.startswith("NN") or \
        token.tag_.startswith("VB") or \
        token.tag_.startswith("JJ") or \
        token.tag_.startswith("RB") or \
        token.tag_.startswith("CD") or \
        token.tag_.startswith("PRP") or \
        token.tag_.startswith("W") or \
        token.tag_.startswith("MD"):
        return True
    else:
        return False

    
def format_headline(s):
    
    headline = nlp(s)
    cleared_headline = [t for t in headline if not t.is_punct]

    formatted_headline =''


    for i, t in enumerate(headline):
        word = t.text

        if not word.isupper() and (not word.isupper() and word.islower()):
            if (len(word) > 3 \
                or t == cleared_headline[0] or t == cleared_headline[-1] \
                or (headline[i-1].text == '\'' and headline[i-1].whitespace_ == '') \
                or is_notional_pos(t) == True and word.lower() not in ["'s", "n't", "'t"] \
                or (headline[i-1].text == '-' and is_notional_pos(headline[i-2]) == True)) \
                or t.dep_ == 'mark':
                formatted_headline += word.title()
            elif (is_notional_pos(t) == False \
                and t != cleared_headline[0] or t != cleared_headline[-1]):
                formatted_headline += word.lower()
        elif is_notional_pos(t) == True and ((not word.islower() and not word.isupper()) or word.istitle()):
            formatted_headline += word
        else:
            formatted_headline += word

        formatted_headline += t.whitespace_
    return formatted_headline
    
    
def accuracy(validation_set):

    correctly_formatted = 0
    with open(validation_set, 'r', encoding='utf-8') as f:
        test_data = json.load(f)

        for i, sample in enumerate(test_data):
            my_result = format_headline(sample[0])        
        
            if my_result == sample[1]:
                correctly_formatted += 1

    accuracy = correctly_formatted / len(test_data)
    return accuracy      


res = accuracy('/home/prj-nlp-2020/tasks/02-structural-linguistics/data/headlines-test-set.json')
res

>>> 0.91
