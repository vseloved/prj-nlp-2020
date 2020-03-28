import spacy
from spacy import displacy
from collections import Counter 

import re 

validation_set = list()
with open('blog2008.txt') as file:
    validation_set = file.readlines()

nlp = spacy.load("en_core_web_md")
syn = "say tell speak claim communicate articulate bring out enunciate state talk utter verbalize vocalize".split()

colls = dict()
for el in syn:
    colls[el] = Counter()

r = re.compile(r"ly ")

def process_sentense(s):
    if not r.search(s):
        return None
    doc = nlp(s)
    for t in doc:
        stem = t.lemma_
        if stem in syn and t.pos_=='VERB':
            n_token = next(t.rights, None)
            for n_token in t.children:
                if n_token.dep_=='advmod':
                    e = n_token.text[-2:]
                    if e=="ly" and not n_token.text==n_token.text.capitalize():
                        return (stem, n_token.pos_, n_token.text, t.text) # position 4 for debug
            return None


# s = validation_set[4666]
# s = "The government still is n't saying definitively but it would appear that they are giving credence to reports that Bhutto was shot to death ."
# process_sentense(s)

for (i, s) in enumerate(validation_set):
    res = process_sentense(s)
    if i % 10000 == 0:
        # logging so I know it's working 
        print(i)
    if res != None:
        found_for = res[0]
        colls_counter = colls[found_for]
        colls_counter[res[2]] += 1
        print("{}-{}-{}-{}".format(i, res[1], res[3], res[2]))
        

for el in colls: 
    print("{}-{}".format(el, colls[el]))