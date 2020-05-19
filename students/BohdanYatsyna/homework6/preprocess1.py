import csv
import json
from random import seed
from random import randint
import random
import spacy
import en_core_web_md
from spacy.tokens import Doc
from tqdm import tqdm, trange
import numpy as np
import re
from spacy.tokenizer import Tokenizer
from spacy.pipeline import Tagger


def shape(word):
    if re.match('[0-9]+(\.[0-9]*)?|[0-9]*\.[0-9]+$', word):
        return 'number'
    elif re.match('\W+$', word):
        return 'punct'
    elif re.match('[A-Z][a-z]+$', word):
        return 'capitalized'
    elif re.match('[A-Z]+$', word):
        return 'uppercase'
    elif re.match('[a-z]+$', word):
        return 'lowercase'
    elif re.match('[A-Z][a-z]+[A-Z][a-z]+[A-Za-z]*$', word):
        return 'camelcase'
    elif re.match('[A-Za-z]+$', word):
        return 'mixedcase'
    elif re.match('__.+__$', word):
        return 'wildcard'
    elif re.match('[A-Za-z0-9]+\.$', word):
        return 'ending-dot'
    elif re.match('[A-Za-z0-9]+\.[A-Za-z0-9\.]+\.$', word):
        return 'abbreviation'
    elif re.match('[A-Za-z0-9]+\-[A-Za-z0-9\-]+.*$', word):
        return 'contains-hyphen'
    return 'other'


def get_rand_sent(buffer):
    if len(buffer) > 4:
        return randint(1, 4)
    else:
        return randint(1, len(buffer))


def feachure_extractor(sent):
    feachure_sent = []
    doc = sent

    for i, word in enumerate(doc):
        features = dict()
        features['word'] = word.text
        features['lemma'] = word.lemma_
        features['pos'] = word.pos_
        features["shape"] = shape(word.text)

        features['dep'] = word.dep_
        features['head_word'] = word.head.text
        features['head_lemma'] = word.head.lemma_
        features['head_pos'] = word.head.pos_

        # features["word-1"] = doc[i - 1].text if i > 0 else "NONE"
        # features["word-2"] = doc[i - 2].text if i - 1 > 0 else "NONE"
        # features["word+1"] = doc[i + 1].text if i + 1 < len(doc) else "NONE"
        # features["word+2"] = doc[i + 2].text if i + 2 < len(doc) else "NONE"

        features["lemma-1"] = doc[i - 1].lemma_ if i > 0 else "NONE"
        features["lemma-2"] = doc[i - 2].lemma_ if i - 1 > 0 else "NONE"
        features["lemma+1"] = doc[i + 1].lemma_ if i + 1 < len(doc) else "NONE"
        features["lemma+2"] = doc[i + 2].lemma_ if i + 2 < len(doc) else "NONE"

        features["pos-1"] = doc[i - 1].pos_ if i > 0 else "NONE"
        features["pos-2"] = doc[i - 2].pos_ if i - 1 > 0 else "NONE"
        features["pos+1"] = doc[i + 1].pos_ if i + 1 < len(doc) else "NONE"
        features["pos+2"] = doc[i + 2].pos_ if i + 2 < len(doc) else "NONE"

        features["shape-1"] = shape(doc[i - 1].text) if i > 0 else "NONE"
        features["shape-2"] = shape(doc[i - 2].text) if i - 1 > 0 else "NONE"
        features["shape+1"] = shape(doc[i + 1].text) if i + 1 < len(doc) else "NONE"
        features["shape+2"] = shape(doc[i + 2].text) if i + 2 < len(doc) else "NONE"

        features["dep-1"] = doc[i - 1].dep_ if i > 0 else "NONE"
        features["dep-2"] = doc[i - 2].dep_ if i - 1 > 0 else "NONE"
        features["dep+1"] = doc[i + 1].dep_ if i + 1 < len(doc) else "NONE"
        features["dep+2"] = doc[i + 2].dep_ if i + 2 < len(doc) else "NONE"

        features["head_pos-1"] = doc[i - 1].head.pos_ if i > 0 else "NONE"
        features["head_pos-2"] = doc[i - 2].head.pos_ if i - 1 > 0 else "NONE"
        features["head_pos+1"] = doc[i + 1].head.pos_ if i + 1 < len(doc) else "NONE"
        features["head_pos+2"] = doc[i + 2].head.pos_ if i + 2 < len(doc) else "NONE"


        #features["parent"] = doc[i].dep_ + "_" + doc[i].head.lemma_
        #features["right-bigram"] = doc[i + 1].text + "_" + doc[i + 2].text if i < (len(doc) - 2) else "NONE"
        feachure_sent.append(features)
    return feachure_sent


def generate_sent_params(sent_num, debug=False):
    lowercase_list = []
    miss_point_list = []

    old_miss_point = None

    for i in range(sent_num):

        if old_miss_point:
            # ловеркейсим тільки коли у попередньому реченні пропущена крапка
            lowercase = randint(0, 1)
        else:
            # якщо нема пропущеної крапки то не ловеркейсим
            lowercase = 0

        # крапка може бути пропущена у  реченнях крім останнього
        miss_point = randint(0, 1) if i != sent_num - 1 else 0

        lowercase_list.append(lowercase)
        miss_point_list.append(miss_point)

        old_miss_point = miss_point

    if debug:
        for i in range(sent_num):
            print("Sent # {} misspoint {} lowercase {}".format(i, miss_point_list[i], lowercase_list[i]))

    return lowercase_list, miss_point_list


def generate_sent_string(buff_list, debug = False):
    token_list = []
    labels_list = []
    lowercases, miss_points = generate_sent_params(len(buff_list), debug = debug)

    for i, sent in enumerate(buff_list):

        doc = nlp(sent)
        tokens = [tok.text for tok in doc]
        labels = [False for i in range(len(doc))]
        if len(tokens) > 1:
            if miss_points[i]:
                del tokens[-1]
                del labels[-1]
                labels[-1] = True
            if lowercases[i]:
                tokens[0] = tokens[0].lower()

        token_list.extend(tokens)
        labels_list.extend(labels)
    return token_list, labels_list


def generate_dataset_string(buff_list, debug = False):
    gen_tokens_labels = {}

    tokens, labels = generate_sent_string(buff_list, debug)
    doc = nlp(' '.join(tokens))
    assert len(doc) == len(labels)

    gen_tokens_labels['tokens'] = feachure_extractor(doc)
    gen_tokens_labels['labels'] = labels

    return gen_tokens_labels


nlp = spacy.load("en_core_web_md")

# white space tokenizer
nlp.tokenizer = Tokenizer(nlp.vocab)

RAW_SENTENCES_FILE = './stripped_masc_sentences.json'
TEST_DATASET = './run-on-test.json'
DATASET_FILE = './dataset.json'


joined_sent_tokens = []
joined_sent_labels = []
dataset = {}

print('Load Raw data...')
with open(RAW_SENTENCES_FILE) as json_file:
    data = json.load(json_file)

dataset['dev'] = {'tokens': [], 'labels': []}
dataset['test'] = {'tokens': [], 'labels': []}

print('Prepearing TEST dataset part...')
with open(TEST_DATASET) as json_file:
    tt = json.load(json_file)
    for t in tqdm(tt, desc="Loading test tokens and labels"):
        temp_sent = []
        temp_label = []
        for item in t:
            temp_sent.append(item[0])
            temp_label.append(item[1])
        doc_test = nlp(' '.join(temp_sent))
        dataset['test']['tokens'].extend(feachure_extractor(doc_test))
        dataset['test']['labels'].extend(temp_label)


buffer = data
### testing my sentence generator

num_sent = get_rand_sent(buffer)

with tqdm(total=len(buffer), desc="Prepearing DEV dataset tokens and labels") as pbar:
    while buffer:
        num_sent = get_rand_sent(buffer)
        joined_sent_tokens_labels = generate_dataset_string(buffer[:num_sent])
        del buffer[:num_sent]
        dataset['dev']['tokens'].extend(joined_sent_tokens_labels['tokens'])
        dataset['dev']['labels'].extend(joined_sent_tokens_labels['labels'])
        pbar.update(num_sent)

print('Write to file dataset...')
with open(DATASET_FILE, 'w') as file:
    json.dump(dataset, file)
print('DONE')
