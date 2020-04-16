import pymorphy2
from collections import Counter 

import tokenize_uk

morph = pymorphy2.MorphAnalyzer(lang='uk')

validation_set = list()
with open('tyhrolovy.txt') as file:
    validation_set = file.readlines()

def find_adjective(m):
    for x in m:
        if 'ADJF' in x.tag:
            return x
    return None

result = Counter()

def add_to_result(l, w):
    result[(l.normal_form, w.normal_form)]+=1

def process_sentence(s):
    tok = tokenize_uk.tokenize_words(s)
    if len(tok)<=1:
        return
    for (i,token) in enumerate(tok): 
        m = morph.parse(token)
        p = m[0]
        if 'NOUN' in p.tag and 'anim' in p.tag:
            left = i-1
            # right = i+1
            if left>=0:
                p_left = find_adjective(morph.parse(tok[left]))
                if p_left:
                    add_to_result(p_left, p)
            # if right<len(tok):
            #     p_right = find_adjective(morph.parse(tok[right]))
            #     if p_right:
            #         add_to_result((token, tok[right]), i)


for i,s in enumerate(validation_set):
    process_sentence(s)

for el in sorted(result.items(), key=lambda item: item[1], reverse=True):
    print("{}: {} {}".format(el[1], el[0][0], el[0][1]))
