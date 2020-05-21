import json
import nltk
import random

with open('run_on_dataset_limited_20k.json', 'w') as w:
    with open('WestburyLab.Wikipedia.Corpus.txt') as f:
        s_pairs_list = []
        s_pairs_count = 0
        for line in f:
            if s_pairs_count > 20000:
                break
            if line.count(".") == 1 or line == "---END.OF.DOCUMENT---\n" or line == "\n":
                continue
            sentences = nltk.sent_tokenize(line.strip("\n"))
            if len(sentences) in (2, 3, 4):
                tokens = []
                for i, s in enumerate(sentences):
                    s_tokens = nltk.word_tokenize(s)
                    if len(s_tokens) > 1:
                        s_pairs = [[t, False] for t in s_tokens]
                        if i != len(sentences) - 1:
                            s_pairs = s_pairs[:-1]
                            s_pairs[-1][1] = True
                        if i > 0 and random.randint(0, 10) > 7:
                            if not s_pairs[0][0].isupper():
                                s_pairs[0][0] = s_pairs[0][0].lower()
                        s_pairs_list.append(s_pairs)
                        s_pairs_count += 1
        json.dump(s_pairs_list, w)
