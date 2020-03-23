import stanza
from tqdm import tqdm
from collections import OrderedDict
from operator import itemgetter

# stanza.download('uk')

nlp = stanza.Pipeline('uk')

with open("../tasks/02-structural-linguistics/data/tyhrolovy.txt") as file:
    data = file.readlines()


cleaned_data = []
word_bigram = {}
for i, d in enumerate(data):
    d = d.rstrip()
    if d == '':
        continue
    cleaned_data.append(d)

for d in tqdm(cleaned_data):
    doc = nlp(d)
    for sentence in doc.sentences:
        for noun_i, word in enumerate(sentence.words):
            if word.text.lower() == "старий":
                t = 1
            if word.pos == "PROPN" or word.upos == "NOUN":
                if 'Animacy=Anim' in word.feats:
                    for w in sentence.words:
                        if w.upos == "ADJ":
                            if w.head == noun_i + 1:
                                try:
                                    word_bigram[word.text.lower() + ' ' + w.text.lower()] += 1
                                except:
                                    word_bigram.update({word.text.lower() + ' ' + w.text.lower(): 1})

word_bigram = dict(OrderedDict(sorted(word_bigram.items(), key=itemgetter(0))))
word_bigram = dict(OrderedDict(sorted(word_bigram.items(), key=itemgetter(1), reverse=True)))

with open('../students/BohdanYatsyna/homework2/task-02-3-2-statistic.txt', 'w') as f:
    for key, value in word_bigram.items():
        print('{}: {}'.format(value, key), file=f)
