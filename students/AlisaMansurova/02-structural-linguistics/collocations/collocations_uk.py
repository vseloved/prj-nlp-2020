import stanfordnlp
import os

absDir = os.path.dirname(os.path.abspath(__file__))
data_dir = '../../../../tasks/02-structural-linguistics/data/'
tasksDir = os.path.join(absDir, data_dir)
TYHROLOVY = os.path.join(tasksDir, 'tyhrolovy.txt')

nlp = stanfordnlp.Pipeline(lang='uk', processors='tokenize,pos,lemma')

with open(TYHROLOVY) as f:
    corpus = [l for l in (line.strip() for line in f) if l]


def find_pairs(doc):
    pairs = []
    for sent in doc.sentences:
        for word in sent.words:

            anim = 'Animacy=Anim' in word.feats
            if anim:
                adj = next((x for x in sent.words if int(x.index) ==
                            int(word.index) - 1 and x.upos == 'ADJ'), None)
                if adj:
                    pairs.append(f'{adj.lemma.lower()} {word.lemma.lower()}')
    return pairs


def order_pairs(pairs):
    with_freq = {x: pairs.count(x) for x in pairs}
    return [
        f'{v}: {k}' for k, v in sorted(with_freq.items(),
                                       key=lambda x: x[1], reverse=True)
    ]


def do_find(corpus):
    res = []
    for prgr in corpus:
        doc = nlp(prgr)
        pairs = find_pairs(doc)
        if pairs:
            res += pairs

    for x in order_pairs(res):
        print(x)


def find_anim_adj_debug(corpus, s, e):
    do_find(corpus[s:e])


def find_anim_adj_all(corpus):
    do_find(corpus)


# main
find_anim_adj_all(corpus)
