import urllib
import requests
import json
import os
import sys
import json

args = sys.argv
chunk = args[1] if len(args) > 1 else None

absDir = os.path.dirname(os.path.abspath(__file__))
train_tokens_file_name = './train_tokens.json'
train_tokens_file = os.path.join(absDir, train_tokens_file_name)
test_data_file_name = '../../../tasks/06-language-as-sequence/run-on-test.json'
test_data_file = os.path.join(absDir, test_data_file_name)
unique_words_file_name = f'./unique_words_{chunk}.txt' \
    if chunk else f'./unique_words.txt'
unique_words_file = os.path.join(absDir, unique_words_file_name)
ngrams_file_name = f'./trigrams_{chunk}.txt'\
    if chunk else f'./trigrams.txt'
ngrams_file = os.path.join(absDir, ngrams_file_name)

API_SEARCH_URL = 'https://api.phrasefinder.io/search?'

ngrams_keys = ['tks', 'mc', 'vc', 'id', 'sc']

with open(train_tokens_file) as f:
    train_tokens = json.load(f)


def normalize_word(word):
    return word.replace(
        '"', '').replace('\'', '').replace('\n', '').replace('\t', '')


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


def get_ngrams(words):
    with open(ngrams_file, 'a') as f:
        ngrams = []

        for i, word in enumerate(words):
            query = urllib.parse.quote(f'{word}??')
            params = {'corpus': 'eng-us', 'query': query,
                      'topk': 3, 'format': 'tsv'}
            params = '&'.join('{}={}'.format(name, value)
                              for name, value in params.items())
            response = requests.get(API_SEARCH_URL + params)
            # resp = json.loads(response.text)
            resp = response.text
            # if resp.get('phrases'):
            #     phrases = resp['phrases']
            #     if phrases:
            #         res = [{k: x[k] for k in ngrams_keys} for x in phrases]
            #         ngrams.append(res)
            # else:
            #     print(f'Smth wrong with word {word}:', response.text)

            print('<<<<', i)
            f.write(resp)
        # f.write(json.dumps([x for sub in ngrams for x in sub]))


# get_words_for_ngrams(train_tokens)

with open(unique_words_file) as f:
    words = f.readlines()
    get_ngrams(words)
