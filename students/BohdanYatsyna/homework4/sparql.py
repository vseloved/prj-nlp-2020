import re
import csv
import wikipediaapi

import spacy
nlp = spacy.load("en_core_web_md")


actors = "Brad Pitt"

wiki_wiki = wikipediaapi.Wikipedia('en')

page_py = wiki_wiki.page(actors)
splitted_text = page_py.text.split('\n')

for line in splitted_text:
    doc = nlp(line)
    #for sent in doc.sents:
    print("== Sentense ==")
    print(line)
    for ent in line.ents:
        print(ent)
        if ent.label_ == "EVENT":
            print(ent.text)

#page_py = wiki_wiki.page(actors)

t =1

