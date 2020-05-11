
import random
import os
import spacy
import re
import json
import sys
from functools import reduce

args = sys.argv
chunk = args[1] if len(args) > 1 else None

nlp = spacy.load('en_core_web_md')

absDir = os.path.dirname(os.path.abspath(__file__))
extracted_data_file_name = './extracted_data.json'
extracted_data_file = os.path.join(absDir, extracted_data_file_name)
train_tokens_file_name = './train_tokens.json'
train_tokens_file = os.path.join(absDir, train_tokens_file_name)
train_data_file_name = './train_data_glued.json'
train_data_file = os.path.join(absDir, train_data_file_name)
test_data_file_name = '../../../tasks/06-language-as-sequence/run-on-test.json'
test_data_file = os.path.join(absDir, test_data_file_name)
unique_words_file_name = f'./unique_words_{chunk}.txt' \
    if chunk else f'./unique_words.txt'
unique_words_file = os.path.join(absDir, unique_words_file_name)
ngrams_file_name = f'./trigrams_{chunk}.txt'\
    if chunk else f'./trigrams.txt'
ngrams_file = os.path.join(absDir, ngrams_file_name)


""" Functions to prepare train data """


def get_all_data(root, results_file_path):
    def sp(text):
        return reduce(lambda acc, el: acc[:-1] + [(acc[-1].strip() if acc else '') + el]
                      if el and re.findall('[\\.\\?\\!]+', el)
                      else acc + [el.strip()], re.split('([\\.\\?\\!]+)(?=\\s)', text),
                      [])

    for root, subdirs, files in os.walk(root):
        res = []
        src_files = [x for x in files if x.endswith('.txt')]
        for file in src_files:
            file_path = os.path.join(root, file)
            with open(file_path) as f:
                content = f.read()

                content = re.sub('\\s{2,}', ' ', content.replace(
                    '\n ', ' ').replace('\n', ' '))
                content = sp(content)
                for sent in content:
                    res.append(sent)
        with open(results_file_path, 'w') as f:
            f.write(json.dumps(res))
    return res


def generate_glued_sents(text):
    tokens = []
    labels = []
    num_sents = random.randint(2, 4)
    text_split = [text[i:i+num_sents] for i in range(0, len(text), num_sents)]

    for spl in text_split:
        sents_spl = spl
        out_of_seq = num_sents
        num_lower = random.randint(0, out_of_seq)
        if num_lower < len(sents_spl):
            sent_to_lower = sents_spl[num_lower]
            s_lower = sent_to_lower[:1].lower() + sent_to_lower[1:]
            sents_spl[num_lower] = s_lower

        for i, sent in enumerate(sents_spl):
            doc = nlp(sent)

            eos_syms = ['.', '?', '!', '...']
            for token in doc:
                ln = len(doc)
                if token.i == ln - 2 and token.i + 1 < ln and doc[token.i + 1].text in eos_syms:
                    labels.append(True)
                    tokens.append(token)
                else:
                    if token.text not in eos_syms:
                        labels.append(False)
                        tokens.append(token)

    return tokens, labels


def get_glued_data(train_data, results_file_path):
    tokens, labels = generate_glued_sents(train_data)
    with open(results_file_path, 'w') as f:
        f.write(json.dumps([x.text for x in tokens]))
    return tokens, labels


def get_train_data(extracted_data_file, train_data_file):
    with open(extracted_data_file) as f:
        extracted_data = json.load(f)
    return get_glued_data(extracted_data, train_data_file)


def get_test_data(text):
    sents = [x for sub in text for x in sub]
    test_tokens = [x[0] for x in sents]
    test_labels = [x[1] for x in sents]

    return test_tokens, test_labels


""" Various debug functions and helpers for train data preparation """


def split_unique_words_into_chunks(filename):
    SIZE = 500
    with open(f'{filename}.txt') as f:
        lines = f.readlines()
        ln = len(lines)
        for i in range(1, int(ln/SIZE) + 2):
            end = i*SIZE
            if end > ln:
                start = (i - 1)*SIZE + 1
                chunk = lines[start:]

            else:
                start = (i - 1)*SIZE + 1 if i > 1 else 0
                chunk = lines[start:end]
            with open(f'./{filename}_{i}.txt', 'w') as ch:
                ch.writelines(chunk)


def get_words_for_ngrams(train_tokens):
    with open(test_data_file) as f:
        test_data = json.load(f)

    syms = ['.', '?', '!', '...', ',', ':', ';',
            '-', '>', '<', '&', '(', '=', '/', '\\', '[', '{']

    words = [x[0] for sub in test_data for x in sub]
    with open(unique_words_file, 'a') as f:
        for i, token in enumerate(train_tokens):
            if token not in words and token not in syms:
                words.append(token)
                f.write(token + '\n')
            print('>>>>>', i)


def merge_gnrams_from_chuks(num_chunks):
    res = []
    for i in range(1, num_chunks):
        with open(f'./trigrams_{i}.txt') as f:
            content = f.readlines()
            res += content
    with open(f'./trigrams.txt', 'w') as f:
        f.writelines(res)


def tsv_to_json(content):
    res = []
    for line in content:
        if line.startswith('{"error"'):
            continue
        obj = {'tks': []}
        parts = line.split()
        for x in [parts[0], parts[1], parts[2]]:
            r = re.split('_(\\d)', x)
            obj['tks'].append({'tt': r[0], 'tg': r[1]})
        obj['mc'] = parts[3]
        obj['vc'] = parts[4]
        obj['sc'] = parts[8]
        res.append(obj)
    return res


""" main """

train_tokens, train_labels = get_train_data(
    extracted_data_file, train_data_file)

with open(test_data_file) as f:
    test_content = json.load(f)
    test_tokens, test_labels = get_test_data(test_content)
