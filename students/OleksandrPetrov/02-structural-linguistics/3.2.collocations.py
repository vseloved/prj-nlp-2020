#!/usr/bin/env python

import os
import io
import collections
import time
import datetime as dt

import stanza

HERE = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(HERE, '..', '..', '..', 'tasks', '02-structural-linguistics', 'data')


def find_collocations(doc):

    for s in doc.sentences:
        for w in s.words:
            if w.upos != 'ADJ':
                continue
            try:
                head = s.words[w.head]
            except IndexError:
                # didn't come out how to resolve these errors
                print('Error:', w.pretty_print())
                continue
            else:
                if head.upos != 'PROPN':
                    continue
                yield (w.lemma, head.lemma)


def load_uk_text_lines():
    data_file_path = os.path.join(DATA_DIR, 'tyhrolovy.txt')
    with io.open(data_file_path, 'rt', encoding='utf-8') as text_istream:
        samples = []
        for line in text_istream:
            input_text = line.strip()
            if not input_text:
                continue
            samples.append(input_text)
        return samples


def process(doc):

    stats = collections.Counter(find_collocations(doc))

    print('=' * 80)
    for (adj, propn), n in stats.most_common():
        print('{}: {} {}'.format(n, adj, propn))


def main():

    nlp = stanza.Pipeline('uk', use_gpu=False, verbose=False)
    print('Model loaded.')

    samples = load_uk_text_lines()
    # samples = samples[:200]

    print('Going to process lines:', len(samples))

    text = '\n\n'.join(samples)  # for [sanza] batch processing

    print('[nlp] processing...')
    beg = time.monotonic()
    doc = nlp(text)
    end = time.monotonic()
    elapsed = dt.timedelta(seconds=(end - beg))
    print('[nlp] finished in {}'.format(elapsed))

    process(doc)


if __name__ == '__main__':
    main()
