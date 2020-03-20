import spacy
from spacy import displacy
from collections import Counter 
validation_set = list()
with open('blog2008.txt') as file:
    validation_set = file.readlines()

nlp = spacy.load("en_core_web_sm")
syn = "say tell speak claim communicate articulate bring out enunciate state talk utter verbalize vocalize".split()

colls = dict()
for el in syn:
    colls[el] = Counter()

def process_sentense(s):
    doc = nlp(s)
    for t in doc:
        if t.text in syn and t.pos_=='VERB':
            n_token = next(t.rights, None)
            if n_token:
                e = n_token.text[-2:]
                if e=="ly":
                    return (t.text, n_token.pos_, n_token.text)
            else:
                return None


# s = validation_set[4666]
# process_sentense(s)
for (i, s) in enumerate(validation_set):
    res = process_sentense(s)
    if i % 1000 == 0:
        print(i)
    if res != None:
        found_for = res[0]
        colls_counter = colls[found_for]
        colls_counter[res[2]] += 1
        print("{}-{}-{}-{}".format(i, res[1], res[0], res[2]))
        

for el in colls: 
    print("{}-{}".format(el, colls[el]))