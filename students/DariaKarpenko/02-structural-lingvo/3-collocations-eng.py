import nltk
from nltk import FreqDist
from nltk.corpus import wordnet 
from collections import defaultdict
import spacy
nlp = spacy.load('en_core_web_md', disable=['textcat', 'ner'])

all_synonyms = []
verbs_list = ["say", "tell", "speak", "claim", "communicate"]
for verb in verbs_list:
    for syn in wordnet.synsets(verb):
        for lm in syn.lemmas():
            if syn.pos() =='v':
                all_synonyms.append(lm.name())
all_synonyms = set(all_synonyms)


def verb_adverb(lines):
    adverbs = defaultdict(list)
    for line in lines:
            tokens = nlp(line)
            for token in tokens:
                if token.tag_.startswith('VB') and token.lemma_ in all_synonyms:
                    for child in token.children:
                        if child.text.endswith('ly') and child.tag_.startswith('RB'): #and child.dep_ == 'advmod':
                            adverbs[token.lemma_].append(child.lemma_)
                            for grandchild in child.children:
                                if grandchild.text.endswith('ly') and grandchild.tag_.startswith('RB'):
                                    adverbs[token.lemma_].append(grandchild.lemma_)
    return adverbs


final_collocations = {}
with open('/home/dasha/Загрузки/blog2008.txt', 'r') as f:
    lines = f.readlines()
    v_adv_collocs = verb_adverb(lines)
    
    for key in v_adv_collocs.keys():
        fd = FreqDist(v_adv_collocs[key]).most_common(10)
        final_collocations[key] = fd
    
for v, adv in final_collocations.items():
    print(v, adv)
