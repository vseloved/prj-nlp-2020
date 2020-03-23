import spacy
from tqdm import tqdm
from collections import OrderedDict
from operator import itemgetter

nlp = spacy.load("en_core_web_md")

with open("../tasks/02-structural-linguistics/data/blog2008.txt") as file:
    data = file.readlines()

say = ["say", "tell", "speak", "claim", "communicate", "add", "announce", "answer", "assert", "articulate", "convey",
       "declare", "deliver", "disclose", "do", "enunciate", "estimate", "express", \
       "maintain", "mention", "order", "pronounce", "read", "repeat", "reply", "report", "respond", "reveal", "state",
       "suggest", "suppose", "voice", \
       "talk", "verbalize", "vocalize"]
count = 0
word_pair_freq = {}

for d in tqdm(data):
    doc = nlp(d)
    for token in doc:
        if token.pos == 86 and token.text[-2:] == "ly" and \
                token.head.pos == 100 and token.head.text in say:
            count += 1

            try:
                word_pair_freq[token.head.text.lower()][token.text.lower()] += 1
            except KeyError:

                if word_pair_freq.get(token.head.text.lower(), False):
                    word_pair_freq[token.head.text.lower()].update({token.text.lower(): 1})
                else:
                    word_pair_freq[token.head.text.lower()] = {token.text.lower(): 1}

word_pair_freq = dict(OrderedDict(sorted(word_pair_freq.items(), key=itemgetter(0))))

for key, value in word_pair_freq.items():
    word_pair_freq[key] = dict(OrderedDict(sorted(word_pair_freq[key].items(), key=itemgetter(1), reverse=True)))

with open('../students/BohdanYatsyna/homework2/task-02-3-statistic.txt', 'w') as f:
    for key, value in word_pair_freq.items():
        print('{}: {}'.format(key, value),file=f)
