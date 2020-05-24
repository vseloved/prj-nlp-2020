import json
from random import randint
from random import seed

import spacy
from tqdm import tqdm

nlp = spacy.load("en_core_web_md")
RAW_SENTENCES_FILE = '../stripped_masc_sentences.json'
TEST_DATASET = './run-on-test.json'
DATASET_FILE = './dataset.json'

joined_sent_tokens = []
joined_sent_labels = []
dataset = {}
with open(RAW_SENTENCES_FILE) as json_file:
    data = json.load(json_file)

dataset['dev'] = {'tokens': [], 'labels': []}
dataset['test'] = {'tokens': [], 'labels': []}

with open(TEST_DATASET) as json_file:
    tt = json.load(json_file)
    for t in tt:
        temp_sent = []
        temp_label = []
        for item in t:
            temp_sent.append(item[0])
            temp_label.append(item[1])
        dataset['test']['tokens'].append(temp_sent)
        dataset['test']['labels'].append(temp_label)

seed(40)


def get_rand_sent(buf):
    if len(buffer) > 4:
        return randint(1, 4)
    else:
        return randint(1, len(buffer))


def generate_dataset_string(buff_list):
    print('len {}   {}'.format(len(buff_list), buff_list))
    gen_tokens_labels = {}

    for item in buff_list:
        doc = nlp(item)
        first_cap = randint(0, 1)
        miss_point = randint(0, 1)
        gen_tokens_labels['tokens'] = []
        gen_tokens_labels['labels'] = []

        for i, token in enumerate(doc):
            if not i and not first_cap:
                gen_tokens_labels['tokens'].append(token.text.lower())
                gen_tokens_labels['labels'].append(False)
            elif i == len(doc) - 1 and token.pos_ == 'PUNCT' and miss_point:
                gen_tokens_labels['labels'][-1] = True
            else:
                gen_tokens_labels['tokens'].append(token.text)
                gen_tokens_labels['labels'].append(False)

    return gen_tokens_labels


buffer = data
while tqdm(buffer):
    num_sent = get_rand_sent(buffer)
    joined_sent_tokens_labels = generate_dataset_string(buffer[:num_sent])
    del buffer[:num_sent]
    dataset['dev']['tokens'].append(joined_sent_tokens_labels['tokens'])
    dataset['dev']['labels'].append(joined_sent_tokens_labels['labels'])

with open(DATASET_FILE, 'w') as file:
    json.dump(dataset, file)
