import nltk
import json
from random import choice,randint

files = nltk.corpus.gutenberg.fileids()

sent_count = [2,3,4]

with open('gutenberg_dataset.json','w') as w:
    s_pairs_list = []
    for file in files:
        sentences = nltk.corpus.gutenberg.sents(file) 
        sents_to_merge = []
        count = choice(sent_count)
        c = 0
        for sent in sentences:
            sent = nltk.word_tokenize(" ".join(sent))
            if c < count:
                sents_to_merge.append(sent)
                c += 1
            else:
                c = 0
                count = choice(sent_count)
                for i,s_tokens in enumerate(sents_to_merge):
                    if len(s_tokens) > 1:
                        s_pairs = [[t, False] for t in s_tokens]
                        if i != len(sents_to_merge) - 1:
                            s_pairs = s_pairs[:-1]
                            s_pairs[-1][1] = True
                            if i > 0 and randint(0, 10) > 7:
                                if not s_pairs[0][0].isupper():
                                    s_pairs[0][0] = s_pairs[0][0].lower()
                            s_pairs_list.append(s_pairs)
                    else:
                        break
                sents_to_merge = []
    json.dump(s_pairs_list, w)