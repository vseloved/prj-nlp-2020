import spacy
from spacy import displacy
import en_core_web_lg
import helpers
import json
import os
from tqdm import tqdm
import re

class pureHeader:
    nlp = spacy.load("en_core_web_md")

    def __init__(self, text):
        self.modified_text = self.rules(text)


    def rules(self, text):
        '''
        Модифікує string таким чином щоб літери слова довжиною 4 були з великої букви.
        :param text: текст
        :return : модіфікований текст
        '''

        modified_text = ""
        doc = pureHeader.nlp(text)

        for i, token in enumerate(doc):

            is_capitalize = False
            is_lowercased = False

            # rule_fourLonger check
            if len(token) > 3:
                is_capitalize = True
            # check if NER dont change word
            if token.ent_type_ == 'ORG':
                modified_text += token.text + token.whitespace_
                continue

            # chek if word have couple of cappital letters

            if len(re.findall(r'[A-Z]',token.text))>1:
                modified_text += token.text + token.whitespace_
                continue

            #rule_rule_capFirstLast check
            if i == len(doc) - 1 or i == 0:
                is_capitalize = True

            if i == 1:
                if doc[0].text == '\'':
                    modified_text += token.text.capitalize() + token.whitespace_
                    continue
            # rule_forLangParts check
            if token.pos_ == "NOUN": is_capitalize = True
            if token.pos_ == "PRON": is_capitalize = True
            if token.pos_ == "VERB": is_capitalize = True
            if token.pos_ == "ADJ": is_capitalize = True
            if token.pos_ == "ADV": is_capitalize = True
            if token.pos_ == "SCONJ" and token.dep_ != 'prep' : is_capitalize = True
            if token.pos_ == "NUM" : is_capitalize = True

            if token.shape_ == "'x":
                modified_text += token.text + token.whitespace_
                continue

            if token.lemma_ == 'be':
                modified_text += token.text.capitalize() + token.whitespace_
                continue
            # rule fo 'Is' -
            if token.pos_ == "AUX":
                t=1


            # rule for ''s' - case
            if token.pos_ == "AUX" and token.dep_ == 'case':
                modified_text += token.text + token.whitespace_
                continue

            # rule_forDash check
            if i > 0 and i < len(doc) - 1:
                if doc[i + 1].text == '-': is_capitalize = True
                if doc[i - 1].text == '-': is_capitalize = True

            # rule_forOther check
            if token.pos_ == "DET": is_lowercased = True
            if token.pos_ == "CONJ":  is_lowercased = True
            if token.pos_ == "CCONJ": is_lowercased = True
            if token.pos_ == "ADP": is_lowercased = True

            if token.pos_ == "PART":
                if token.text == "not" or token.text == "Not":
                    modified_text += token.text.capitalize() + token.whitespace_
                    continue
                else:
                    is_lowercased = True


            if token.pos_ == "INTJ": is_lowercased = True

            # применение правил
            if is_capitalize == True:
                if token.text.isupper() == True:
                    modified_text += token.text + token.whitespace_
                else:
                    modified_text += token.text.capitalize() + token.whitespace_
            else:
                if is_lowercased == True:
                    modified_text += token.text.lower() + token.whitespace_
                else:
                    modified_text += token.text + token.whitespace_

        return modified_text

def accuracy(file):

    modified_text = ""
    data = {}
    correct_headers = 0

    with open(file) as json_file:
        data = json.load(json_file)

    for i, d in tqdm(enumerate(data)):
        h = pureHeader(d[0])
        if h.modified_text == d[1]:
            correct_headers += 1


    print('Header accuracy  {:2.2%}'.format(correct_headers/len(data)))



accuracy('../tasks/02-structural-linguistics/data/headlines-test-set.json')

modified_text = ""
data = {}
correct_headers = 0

with open('../tasks/02-structural-linguistics/data/headlines-test-set.json') as json_file:
    data = json.load(json_file)

for i, d in enumerate(data):
    h = pureHeader(d[0])
    if h.modified_text == d[1]:
        correct_headers += 1
    else:
        print('number {}\tbase text     \t\t{}'.format(i,d[0]))
        print('number {}\tcorrect header\t\t{}'.format(i,d[1]))
        print('number {}\tpure header \t\t{}'.format(i,h.modified_text))


