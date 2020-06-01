from conllu import parse
from collections import OrderedDict
from spacy import displacy

PATH = 'UD_Ukrainian-IU'

ROOT = OrderedDict([('id', 0), ('form', 'ROOT'), ('lemma', 'ROOT'), ('upostag', 'ROOT'),
                    ('xpostag', None), ('feats', None), ('head', None), ('deprel', None),
                    ('deps', None), ('misc', None)])

def load_treebank(file):
    with open(PATH + '/' + file) as f:
        data = f.read()

    return parse(data)

def print_tree(tree):
    for node in tree:
        head = node['head']
        print('{} <-- {}'.format(node['form'], tree[head - 1]['form'] if head > 0 else 'root'))

def golden_rels(tree):
    return [(node['head'], node['id']) for node in tree]

def intersect(s1, s2):
    return len(set(s1).intersection(set(s2)))

def uas_report(golden, predicted):
    total, correct = 0, 0
    for g,p in zip(golden, predicted):
        total += len(g)
        correct += intersect(g, p)
        
    print("Total:", total)
    print("Correct:", correct)
    print("UAS:", round(correct/total, 2))
    
# https://spacy.io/usage/visualizers#manual-usage
def render_tree(tree, jupyter=True, options={}):
    words = []
    arcs = []
    for node in tree:
        words.append({'text': node['form'], 'tag': node['upostag']})        
        head = node['head']

        if head > 0:
            start = (node['id'] if node['id'] < head else head) - 1
            end = (head if node['id'] < head else node['id']) - 1
            direction = 'left' if node['id'] < head else 'right'
            arcs.append({
                'start': start,
                'end': end,
                'dir': direction,
                'label': node['deprel']
            })
    ex = { 'words': words, 'arcs': arcs }
    displacy.render(ex, style='dep', jupyter=jupyter, manual=True, options=options)