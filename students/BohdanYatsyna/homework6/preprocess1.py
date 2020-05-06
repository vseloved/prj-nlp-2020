import csv
import json
from random import seed
from random import randint
import spacy
import en_core_web_md
from spacy.tokens import Doc
from tqdm import tqdm, trange
import numpy as np
import re

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
        features['lema'] = word.lemma_
        features['pos'] = word.pos_
        features["word-1"] = doc[i-1].text if i > 0 else "NONE"
        features["word-2"] = doc[i-1].text if i > 0 else "NONE"

        features['shape'] = shape(word.text)
        features["parent"] = doc[i].dep_ + "_" + doc[i].head.lemma_
        features["right-bigram"] = doc[i+1].text + "_" + doc[i+2].text if i < (len(doc) - 2) else "NONE"
        feachure_sent.append(features)
    return feachure_sent

def generate_dataset_string(buff_list):
    gen_tokens_labels = {}

    for item in buff_list:
        doc = nlp(item)

        first_cap = randint(0,1)
        miss_point =randint(0,1)
        gen_tokens_labels['tokens'] = []
        gen_tokens_labels['labels'] = []
        extracted_features = feachure_extractor(doc)

        for i in range(len(doc)):

            if not i and not first_cap:
                gen_tokens_labels['tokens'].append(extracted_features[i])
                gen_tokens_labels['labels'].append(False)
            elif i== len(doc) -1 and doc[i].pos_ == 'PUNCT' and miss_point:
                gen_tokens_labels['labels'][-1] = True
                t=1
            else:
                gen_tokens_labels['tokens'].append(extracted_features[i])
                gen_tokens_labels['labels'].append(False)

    return gen_tokens_labels

nlp = spacy.load("en_core_web_md")
RAW_SENTENCES_FILE = '../stripped_masc_sentences.json'
TEST_DATASET = './run-on-test.json'
DATASET_FILE = './dataset.json'

joined_sent_tokens = []
joined_sent_labels = []
dataset = {}

print('Load Raw data...')
with open(RAW_SENTENCES_FILE) as json_file:
    data = json.load(json_file)

dataset['dev'] = {'tokens': [],'labels': []}
dataset['test']= {'tokens': [],'labels': []}

print('Prepearing TEST dataset part...')
with open(TEST_DATASET) as json_file:
    tt = json.load(json_file)
    for t in tqdm(tt,desc= "Loading test tokens and labels"):
        temp_sent = []
        temp_label = []
        for item in t:
            temp_sent.append(item[0])
            temp_label.append(item[1])
        #doc_test = nlp(' '.join(temp_sent))
        doc_test = Doc(nlp.vocab, words=temp_sent)
        dataset['test']['tokens'].extend(feachure_extractor(doc_test))
        dataset['test']['labels'].extend(temp_label)

seed(40)

buffer = data

with tqdm(total=len(buffer), desc="Prepearing DEV dataset tokens and labels") as pbar:
    while buffer:
        num_sent = get_rand_sent(buffer)
        joined_sent_tokens_labels = generate_dataset_string(buffer[:num_sent])
        del buffer[:num_sent]
        dataset['dev']['tokens'].extend(joined_sent_tokens_labels['tokens'])
        dataset['dev']['labels'].extend(joined_sent_tokens_labels['labels'])
        pbar.update(num_sent)

print('Write to file dataset...')
with open(DATASET_FILE,'w') as file:
    json.dump(dataset, file)
print('DONE')




