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
        for i, word in enumerate(sentence.words):
            if word.upos == "ADJ":
                if sentence.words[word.head - 1].upos in ["PROPN", "NOUN"] \
                        and 'Animacy=Anim' in sentence.words[word.head - 1].feats:

                    try:
                        word_bigram[sentence.words[word.head - 1].lemma + ' ' + word.lemma] += 1
                    except:
                        word_bigram.update({sentence.words[word.head - 1].lemma + ' ' + word.lemma: 1})

word_bigram = dict(OrderedDict(sorted(word_bigram.items(), key=itemgetter(0))))
word_bigram = dict(OrderedDict(sorted(word_bigram.items(), key=itemgetter(1), reverse=True)))

with open('../students/BohdanYatsyna/homework2/task-02-3-2-statistic.txt', 'w') as f:
    for key, value in word_bigram.items():
        print('{}: {}'.format(value, key), file=f)
