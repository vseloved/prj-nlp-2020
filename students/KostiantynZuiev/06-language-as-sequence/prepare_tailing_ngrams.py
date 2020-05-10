import json


def prepare_tailing_ngrams(ngrams):
    print(len(ngrams))
    current_ngram = ''
    prepared_ngrams = []
    counter = 0
    for ngram in ngrams:
        print(counter)
        counter += 1
        if ngram == current_ngram:
            continue
        else:
            current_ngram = ngram
        tokens = ngram.split('._.')[0].split()
        if len(tokens) >= 2:
            pre_period = tokens[-1].split()[0]
            pre_pre_period = tokens[-2].split()[0]
            pair = (pre_pre_period.split("_")[0], pre_period.split("_")[0])
            prepared_ngrams.append(pair)
    print(len(prepared_ngrams))
    return prepared_ngrams

with open('tailing-5-grams.txt','r') as f:
    ngrams = []
    for line in f:
        ngrams.append(line.strip("\n"))

prepared_ngrams = prepare_tailing_ngrams(ngrams)

with open('prepared-tailing-5-grams.json','w') as w:
    json.dump(prepared_ngrams, w)