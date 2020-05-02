from collections import OrderedDict
from conllu import parse
from enum import Enum
import numpy as np
import json
import os
from sklearn.metrics import classification_report
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import tokenize_uk
import pymorphy2
import stanza


absDir = os.path.dirname(os.path.abspath(__file__))
data_dir_name = '../../../../UD_Ukrainian-IU'
data_dir_path = os.path.join(absDir, data_dir_name)
train_file_path = os.path.join(data_dir_path, 'uk_iu-ud-train.conllu')
test_file_path = os.path.join(data_dir_path, 'uk_iu-ud-train.conllu')


with open(train_file_path) as f:
    train_data = f.read()

with open(test_file_path) as f:
    test_data = f.read()

train_trees = parse(train_data)
test_trees = parse(test_data)


""" Utils """


def compose(*funcs):
    def inner(*arg):
        res = {}
        for f in funcs:
            res.update(f(*arg))
        return res
    return inner


def stringify_feats(token):
    token_feats = token['feats']
    return ';'.join([f'{k}={v}' for k, v in token_feats.items()]) if token_feats else 'NONE'


""" Feature extractors """


def feature_extractor_base(stack, queue, _):
    feat = {}

    if stack:
        top_stack = stack[-1]
        feat['s0-word'] = top_stack['form']
        feat['s0-lemma'] = top_stack['lemma']
        feat['s0-pos'] = top_stack['upostag']
    if (len(stack)) > 1:
        feat['s1-pos'] = stack[-2]['upostag']
    if queue:
        top_queue = queue[0]
        feat['q0-word'] = top_queue['form']
        feat['q0-lemma'] = top_queue['lemma']
        feat['q0-pos'] = top_queue['upostag']
    if (len(queue)) > 1:
        q_next = queue[1]
        feat['q1-word'] = q_next['form']
        feat['q1-pos'] = q_next['upostag']
    if (len(queue)) > 2:
        feat['q2-pos'] = queue[2]['upostag']
    if (len(queue)) > 3:
        feat['q3-pos'] = queue[3]['upostag']

    return feat


def feature_extractor_feats(stack, queue, _):
    feat = {}

    if stack:
        feat['s0-feats'] = stringify_feats(stack[-1])
    if (len(stack)) > 1:
        feat['s1-feats'] = stringify_feats(stack[-2])
    if queue:
        feat['q0-feats'] = stringify_feats(queue[0])
    if (len(queue)) > 1:
        feat['q1-feats'] = stringify_feats(queue[1])

    return feat


def feature_extractor_deprels(stack, queue, relations):
    def _get_ldep_rdep(id, relations):
        left = 100500
        right = -1
        ldep = 'NONE'
        rdep = 'NONE'
        for (ch, head, rel) in relations:
            if head == id:
                if (ch < head) and (ch < left):
                    left = ch
                    ldep = rel
                if (ch > head) and (ch > right):
                    right = ch
                    rdep = rel
        return ldep, rdep

    feat = {}
    if stack:
        top_stack = stack[-1]
        feat['s0-deprel'] = top_stack['deprel'] or 'NONE'
        ldep, rdep = _get_ldep_rdep(top_stack['id'], relations)
        feat['s0-ldep'] = ldep
        feat['s0-rdep'] = rdep
    if queue:
        top_queue = queue[0]
        feat['q0-deprel'] = top_queue['deprel'] or 'NONE'
        ldep, rdep = _get_ldep_rdep(top_queue['id'], relations)
        feat['q0-ldep'] = ldep
        feat['q0-rdep'] = rdep

    return feat


def feature_extractor_path_to_root(stack, queue, relations):
    def get_path_to_root(id, relations):
        curr_ch = id
        steps = 0
        rels_sorted = sorted(relations, key=lambda x: x[0] == id, reverse=True)
        for (ch, head, rel) in rels_sorted:
            if curr_ch == ch:
                steps = + 1
                curr_ch = head
        return steps

    feat = {}
    if stack:
        top_stack = stack[-1]
        feat['s0-path-root'] = get_path_to_root(top_stack['id'], relations)
    if queue:
        top_queue = queue[0]
        feat['q0-path-root'] = get_path_to_root(top_queue['id'], relations)

    return feat


def feature_extractor_dep_feats(stack, queue, relations):
    def get_ldep_rdep_feats(id, relations, tokens):
        left = 100500
        right = -1
        lfeat = 'NONE'
        rfeat = 'NONE'
        for (ch, head, _) in relations:
            if head == id:
                if (ch < head) and (ch < left):
                    left = ch
                if (ch > head) and (ch > right):
                    right = ch

        l_tok = next((x for x in tokens if x['id'] == left), None)
        r_tok = next((x for x in tokens if x['id'] == right), None)
        if l_tok:
            lfeat = stringify_feats(l_tok)
        if r_tok:
            rfeat = stringify_feats(r_tok)

        return lfeat, rfeat

    feat = {}
    if stack:
        top_stack = stack[-1]
        ldep_f, rdep_f = get_ldep_rdep_feats(top_stack['id'], relations, stack)
        feat['s0-ldep-feats'] = ldep_f
        feat['s0-rdep-feats'] = rdep_f
    if queue:
        top_queue = queue[0]
        ldep_f, rdep_f = get_ldep_rdep_feats(top_queue['id'], relations, stack)
        feat['q0-ldep-feats'] = ldep_f
        feat['q0-rdep-feats'] = rdep_f

    return feat


""" Parser """


class Actions(str, Enum):
    SHIFT = 'shift'
    REDUCE = 'reduce'
    RIGHT = 'right'
    LEFT = 'left'


ROOT = OrderedDict([('id', 0), ('form', 'ROOT'), ('lemma', 'ROOT'), ('upostag', 'ROOT'),
                    ('xpostag', None), ('feats',
                                        None), ('head', None),  ('deprel', None),
                    ('deps', None), ('misc', None)])


# the very basic variant of deprels oracle
# TODO: improve it!
def predict_deprel(child, head, tokens):
    ch_pos = child['upostag']
    head_pos = head['upostag'] if not type(head) == str else head

    def is_noun(tag):
        return tag == 'NOUN'

    def is_noun_or_pnoun(tag):
        return tag == 'NOUN' or tag == 'PNOUN'

    def get_ch_child(ch):
        return next((x for x in tokens if x.get('head') and x['head'] == ch['id']), None)

    if head_pos == 'root':
        return 'root'
    elif is_noun(head_pos) and is_noun(ch_pos) or head_pos == 'DET' and is_noun(ch_pos):
        ch_child = get_ch_child(child)
        if ch_child and ch_child['upostag'] == 'PUNCT':
            return 'appos'
        return 'nmod'
    elif (is_noun_or_pnoun(head_pos) or head_pos == 'PRON') and ch_pos == 'ADP':
        return 'case'
    elif head_pos == 'ADJ' and ch_pos == 'ADV' or head_pos == 'VERB' and ch_pos == 'ADV':
        return 'advmod'
    elif is_noun_or_pnoun(head_pos) and ch_pos == 'ADJ':
        return 'amod'
    elif ch_pos == 'PUNCT':
        return 'punct'
    elif ch_pos == 'CCONJ':
        return 'cc'
    elif head_pos == 'PROPN' and ch_pos == 'PROPN':
        ch_child = get_ch_child(child)
        if not ch_child:
            return 'flat:name'
        if ch_child and ch_child['upostag'] == 'CCONJ':
            return 'conj'
        return 'flat:title'
    elif head_pos == 'NOUN' and ch_pos == 'PROPN':
        ch_child = get_ch_child(child)
        if ch_child:
            kid = get_ch_child(ch_child)
            if ch_child['upostag'] == 'PROPN' and not kid or kid and kid['upostag'] == 'CCONJ':
                return 'nmod'
        return 'flat:title'
    elif head_pos == 'VERB' and (ch_pos == 'NOUN' or ch_pos == 'PRON') \
            or head_pos == 'DET' and ch_pos == 'PRON':
        ch_child = get_ch_child(child)
        if ch_child:
            if ch_child['upostag'] == 'ADP':
                return 'obl'
            return 'nsubj'
        else:
            if ch_pos == 'PRON':
                return 'nsubj'
        return 'obj'
    elif head_pos == 'VERB' and ch_pos == 'VERB':
        ch_child = get_ch_child(child)
        if ch_child and ch_child['upostag'] == 'PUNCT':
            return 'advcl'
        return 'xcomp'
    elif head_pos == 'ADV' and ch_pos == 'PART':
        return 'discourse'
    elif head_pos == 'NOUN' and ch_pos == 'DET':
        return 'det'
    elif head_pos == 'NOUN' and ch_pos == 'VERB':
        return 'acl'
    elif head_pos == 'NOUN' and ch_pos == 'SCONJ':
        return 'mark'
    elif head_pos == 'VERB' and ch_pos == 'ADJ':
        return 'advcl:sp'
    elif head_pos == 'ADJ' and ch_pos == 'NOUN':
        ch_child = get_ch_child(child)
        if ch_child and ch_child['upostag'] == 'PUNCT':
            return 'advcl'
        return 'obj'


def oracle(stack, top_queue, relations):
    """
    Make a decision on the right action to do.
    """
    top_stack = stack[-1]
    # check if both stack and queue are non-empty
    if top_stack and not top_queue:
        return Actions.REDUCE
    # check if there are any clear dependencies
    elif top_queue['head'] == top_stack['id']:
        return Actions.RIGHT
    elif top_stack['head'] == top_queue['id']:
        return Actions.LEFT
    # check if we can reduce the top of the stack
    elif top_stack['id'] in [i[0] for i in relations] and \
        (top_queue['head'] < top_stack['id'] or
         [s for s in stack if s['head'] == top_queue['id']]):
        return Actions.REDUCE
    # default option
    else:
        return Actions.SHIFT


def dep_parse(tree, clf, vectorizer, feature_extractor):
    stack, queue, relations = [ROOT], tree[:], []

    while queue or stack:
        if stack and not queue:
            stack.pop()
        else:
            features = feature_extractor(stack, queue, relations)
            action = clf.predict(vectorizer.transform([features]))[0]

            if action == Actions.SHIFT:
                stack.append(queue.pop(0))
            elif action == Actions.REDUCE:
                stack.pop()
            elif action == Actions.LEFT:
                deprel = stack[-1]['deprel'] or predict_deprel(
                    stack[-1], queue[0], stack + queue)
                rel = (stack[-1]['id'], queue[0]['id'], deprel)
                relations.append(rel)
                stack.pop()
            elif action == Actions.RIGHT:
                deprel = queue[0]['deprel'] or predict_deprel(
                    queue[0], stack[-1], stack + queue)
                rel = (queue[0]['id'], stack[-1]['id'], deprel)
                relations.append(rel)
                stack.append(queue.pop(0))

    return sorted(relations)


""" Data & reporting utils """


def get_data_for_tree(tree, feature_extractor):
    features, labels = [], []
    stack, queue, relations = [ROOT], tree[:], []

    while queue or stack:
        action = oracle(stack if len(stack) > 0 else None,
                        queue[0] if len(queue) > 0 else None,
                        relations)
        features.append(feature_extractor(stack, queue, relations))
        labels.append(action.value)
        if action == Actions.SHIFT:
            stack.append(queue.pop(0))
        elif action == Actions.REDUCE:
            stack.pop()
        elif action == Actions.LEFT:
            deprel = stack[-1]['deprel'] or predict_deprel(
                stack[-1], queue[0], stack + queue)
            rel = (stack[-1]['id'], queue[0]['id'], deprel)
            relations.append(rel)
            stack.pop()
        elif action == Actions.RIGHT:
            deprel = queue[0]['deprel'] or predict_deprel(
                queue[0], stack[-1], stack + queue)
            rel = (queue[0]['id'], stack[-1]['id'], deprel)
            relations.append(rel)
            stack.append(queue.pop(0))

    return features, labels


def get_data(trees, feature_extractor):
    features, labels = [], []
    for tree in trees:
        t_f, t_l = get_data_for_tree(
            [t for t in tree if type(t['id']) == int], feature_extractor)
        features += t_f
        labels += t_l
    return features, labels


def calculate_as(trees, clf, vect, feature_extractor):
    total, tpu, tpl, full_match = 0, 0, 0, 0
    golden_u, golden_l = None, None
    for tree in trees:
        tree = [t for t in tree if type(t['id']) == int]
        golden_all = [(node['id'], node['head'], node['deprel'])
                      for node in tree]
        golden_u = [(x, y) for x, y, _ in golden_all]

        predicted_all = dep_parse(tree, clf, vect, feature_extractor)
        predicted_u = [(x, y) for x, y, _ in predicted_all]

        total += len(tree)
        tpu += len(set(golden_u).intersection(set(predicted_u)))
        tpl += len(set(golden_all).intersection(set(predicted_all)))

        if set(golden_all) == set(predicted_all):
            full_match += 1

    print('== Attachment score report ==')
    print('Total: ', total)
    print('Match unlabeled: ', tpu)
#     print('Match labeled: ', tpl)
    print('UAS: ', round(tpu/total, 2))
#     print('LAS: ', round(tpl/total, 2))
    print("Full match:", round(full_match/len(trees), 2))


def get_lrc_classifier():
    pipe = Pipeline([
        ('dict_vect', DictVectorizer()),
        ('lrc', LogisticRegression(random_state=42, multi_class='multinomial',
                                   max_iter=100, solver='sag', n_jobs=20))])

    return pipe


def print_result(train_trees, test_trees, clf, feature_extractor):
    train_feat, train_lab = get_data(train_trees, feature_extractor)
    test_feat, test_lab = get_data(test_trees, feature_extractor)

    clf.fit(train_feat, train_lab)
    print(classification_report(test_lab, clf.predict(test_feat)))
    calculate_as(test_trees, clf['lrc'], clf['dict_vect'], feature_extractor)


""" Main """
clf = get_lrc_classifier()

# baseline
print_result(train_trees, test_trees, clf, feature_extractor_base)

# iteration 1 (with features)
feature_extractor = compose(feature_extractor_base, feature_extractor_feats)
print_result(train_trees, test_trees, clf, feature_extractor)

# iteration 2 (with deprels)
feature_extractor = compose(feature_extractor_base, feature_extractor_feats,
                            feature_extractor_deprels)
print_result(train_trees, test_trees, clf, feature_extractor)

# iteration 3 (with deprel features)
feature_extractor = compose(feature_extractor_base, feature_extractor_feats,
                            feature_extractor_deprels, feature_extractor_dep_feats)
print_result(train_trees, test_trees, clf, feature_extractor)

# iteration 4 (with path-to-root)
feature_extractor = compose(feature_extractor_base, feature_extractor_feats,
                            feature_extractor_deprels, feature_extractor_dep_feats,
                            feature_extractor_path_to_root)
print_result(train_trees, test_trees, clf, feature_extractor)


""" Use parser """

morph = pymorphy2.MorphAnalyzer(lang='uk')
nlp = stanza.Pipeline(lang='uk', processors='tokenize,pos,lemma')


def tokenize_text(text):
    return tokenize_uk.tokenize_uk.tokenize_words(text)


DET = ['будь-який', 'ваш', 'ввесь', 'весь', 'все', 'всенький', 'всякий',
       'всілякий', 'деякий', 'другий', 'жадний', 'жодний', 'ин.', 'ін.',
       'інакший', 'інш.', 'інший', 'їх', 'їхній', 'її', 'його', 'кожний',
       'кожній', 'котрий', 'котрийсь', 'кілька', 'мій', 'наш', 'небагато',
       'ніякий', 'отакий', 'отой', 'оцей', 'сам', 'самий', 'свій', 'сей',
       'скільки', 'такий', 'тамтой', 'твій', 'те', 'той', 'увесь', 'усякий',
       'усілякий', 'це', 'цей', 'чий', 'чийсь', 'який', 'якийсь']

PREP = ["до", "на"]

mapping = {"ADJF": "ADJ", "ADJS": "ADJ", "COMP": "ADJ", "PRTF": "ADJ",
           "PRTS": "ADJ", "GRND": "VERB", "NUMR": "NUM", "ADVB": "ADV",
           "NPRO": "PRON", "PRED": "ADV", "PREP": "ADP", "PRCL": "PART"}


def normalize_pos(word):
    if word.tag.POS == "CONJ":
        if "coord" in word.tag:
            return "CCONJ"
        else:
            return "SCONJ"
    elif "PNCT" in word.tag:
        return "PUNCT"
    elif word.normal_form in PREP:
        return "PREP"
    elif word.normal_form in DET:
        return "DET"
    else:
        return mapping.get(word.tag.POS, word.tag.POS) or 'X'


def pym2_to_conllu(tokens):
    id = 1
    res = []
    for token in tokens:
        word = {}
        word['id'] = id
        word['form'] = token.word
        word['lemma'] = token.normal_form
        word['upostag'] = normalize_pos(token)
        word['feats'] = {'Animacy': token.tag.animacy,
                         'Case': token.tag.case,
                         'Gender': token.tag.gender,
                         'Number': token.tag.number,
                         'Mood': token.tag.mood,
                         'Person': token.tag.person,
                         }
        word['deprel'] = None
        res.append(word)
        id += 1
    return res


def stanza_to_conllu(token):
    res = {}
    res['id'] = int(token.id)
    res['form'] = token.text
    res['lemma'] = token.lemma
    res['upostag'] = token.upos
    res['feats'] = {k: v for k, v in [
        s.split('=') for s in token.feats.split('|')]} if token.feats else None
    res['deprel'] = None
    return res


def parse_sent(text, tokenizer):
    tokens = tokenizer(text)
    relations = dep_parse(tokens, clf['lrc'],
                          clf['dict_vect'], feature_extractor)
    for ch, head, rel in relations:
        print(
            '{} <-- {} -- {}'.format(tokens[ch - 1]['form'], rel,
                                     tokens[head - 1]['form'] if head > 0 else 'ROOT'))


def pym2_tokenizer(text):
    text_tokenized = tokenize_text(text)
    return pym2_to_conllu([morph.parse(w)[0] for w in text_tokenized])


def stanza_tokenizer(text):
    sent = nlp(text).sentences[0]
    return [stanza_to_conllu(t) for t in sent.words]


def parse_text(sents):
    for sent in [sents]:
        print(f'Sentence: {sent}\n')
        print('== pymorphy ==\n')
        parse_sent(sent, pym2_tokenizer)
        print('\n')
        print('== stanza ==\n')
        parse_sent(sent, stanza_tokenizer)
        print('\n\n')


sent_1 = 'Отож ми з ним пiймали в лiсi пугутькало i випустили в клубi пiд час лекцiї \
    на тему "Виховання дiтей у сiм\'ї"'
sent_2 = 'Сінєглазка і Нєзнайка ідуть в просторну уборну, звідки в самом скором врємєні \
    доносяться противні женські п’яні матюки і звуки ляпасів.'
sent_3 = 'Кривавий Пастор гаряче замолився дивною сумішшю нижньонімецької говірки і крепких \
    механізаторських матюків, а фаршрутка, немов космічна комета, летіла крізь промислову зливу, \
        що містила у собі місто Чєлябінськ.'

# use parser

sents = [sent_1, sent_2, sent_3]
parse_text(sents)
