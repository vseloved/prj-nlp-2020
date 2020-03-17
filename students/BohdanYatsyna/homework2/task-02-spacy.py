import spacy
from spacy import displacy
import en_core_web_sm
import helpers
import json
import os
from tqdm import tqdm

class pureHeader:
    nlp = spacy.load("en_core_web_sm")

    def __init__(self, text):
        #self.nlp = spacy.load("en_core_web_sm")
        self.modified_text = self.ruleFourLonger(text)
        self.modified_text = self.ruleCapFirstLast(self.modified_text)
        self.modified_text = self.ruleForLangParts(self.modified_text)
        self.modified_text = self.ruleForDash(self.modified_text)
        self.modified_text = self.ruleForOther(self.modified_text)

    def ruleFourLonger(self, text):
        '''
        Модифікує string таким чином щоб літери слова довжиною 4 були з великої букви.
        :param text: текст
        :return : модіфікований текст
        '''

        modified_text = ""

        doc = pureHeader.nlp(text)

        for token in doc:
            if len(token) > 3:
                modified_text += token.text.capitalize() + token.whitespace_
            else:
                modified_text += token.text + token.whitespace_
        return modified_text


    def ruleCapFirstLast(self, text):
        '''
        Модифікує string таким чином щоб літери першого та останньго слова були з великої букви.
        :param text:
        :return:
        '''

        modified_text = ""
        doc = pureHeader.nlp(text)

        for i, token in enumerate(doc):

            if i == len(doc) - 1 or i == 0:
                modified_text += token.text.capitalize() + token.whitespace_
            else:
                modified_text += token.text + token.whitespace_
        return modified_text


    def ruleForLangParts(self, text):
        '''
        З великої літери потрібно писати іменники (noun), займенники (pronoun), дієслова(verb), прикметники(adjective), прислівники(adverb) та підрядні сполучники.
        :param text:
        :return:
        '''

        modified_text = ""

        doc = pureHeader.nlp(text)

        for token in doc:
            is_capitalize = False

            if token.tag_ == "NOUN": is_capitalize = True
            if token.tag_ == "PRON": is_capitalize = True
            if token.tag_ == "VB": is_capitalize = True
            if token.tag_ == "ADJ": is_capitalize = True
            if token.tag_ == "ADV": is_capitalize = True
            if token.tag_ == "SCONJ": is_capitalize = True

            if is_capitalize == True:
                modified_text += token.text.capitalize() + token.whitespace_
            else:
                modified_text += token.text + token.whitespace_

        return modified_text


    def ruleForDash(self, text):
        '''
        Якщо слово написане через дефіс, велику літеру потрібно додати для кожної частинки слова (наприклад, правильно "Self-Reflection", а не "Self-reflection").
        :param text:
        :return:
        '''

        is_capitalize = False
        modified_text = ""

        doc = pureHeader.nlp(text)

        for i, token in enumerate(doc):
            is_capitalize = False

            if i > 0 and i < len(doc) - 1:
                is_capitalize = True if doc[i + 1].text == '-' else 0
                is_capitalize = True if doc[i - 1].text == '-' else 0

            if is_capitalize == True:
                modified_text += token.text.capitalize() + token.whitespace_
            else:
                modified_text += token.text + token.whitespace_

        return modified_text


    def ruleForOther(self, text):
        '''
        З маленької літери потрібно писати всі інші частини мови: артиклі/визначники (DET), сурядні сполучники(CONJ, CCONJ), прийменники(ADP), частки(PART), вигуки(INTJ).
        :param text:
        :return:
        '''

        is_lowercased = False
        modified_text = ""
        doc = pureHeader.nlp(text)

        for token in doc:
            is_lowercased = False

            if token.tag_ == "DET": is_lowercased = True
            if token.tag_ == "CONJ":  is_lowercased = True
            if token.tag_ == "CCONJ": is_lowercased = True
            if token.tag_ == "ADP": is_lowercased = True
            if token.tag_ == "PART": is_lowercased = True
            if token.tag_ == "INTJ": is_lowercased = True
            if token.tag_ == "TO": is_lowercased = True
            #if token.tag_ == "DT": is_lowercased = True

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

    for d in tqdm(data):
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
    if i == 1:
        t = 1
    h = pureHeader(d[0])
    if h.modified_text == d[1]:
        correct_headers += 1
    else:
        print('number {}\tbase text     \t\t{}'.format(i,d[0]))
        print('number {}\tcorrect header\t\t{}'.format(i,d[1]))
        print('number {}\tpure header \t\t{}'.format(i,h.modified_text))


