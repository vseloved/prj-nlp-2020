#!/usr/bin/env python

import os
import io
import collections
import time
import datetime as dt
import itertools
import re

import spacy

HERE = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(HERE, '..', '..', '..', 'tasks', '02-structural-linguistics', 'data')


def find_collocations(interesting_verbs, doc):

    for token in doc:
        if token.pos != spacy.symbols.ADV:
            continue
        if not token.lemma_.endswith('ly'):
            continue
        parent = token.head
        if parent.pos != spacy.symbols.VERB:
            continue
        if parent.lemma_ not in interesting_verbs:
            continue
        yield (parent.lemma_, token.lemma_)


def load_blog_texts():
    data_file_path = os.path.join(DATA_DIR, 'blog2008.txt')
    with io.open(data_file_path, 'rt', encoding='utf-8') as text_istream:
        samples = []
        for line in text_istream:
            input_text = line.strip()
            samples.append(input_text)
        return samples


def log_progress_iterator(name, n, iterable):
    prefix = '[{}] '.format(name)
    print(prefix + '... starting to process items ...')
    beg = time.monotonic()
    i = 0
    for obj in iterable:
        yield obj
        i += 1
        if i % n == 0:
            current = time.monotonic()
            elapsed = dt.timedelta(seconds=(current - beg))
            print(prefix + '... items processed:', i, 'elapsed:',elapsed)
    end = time.monotonic()
    elapsed = dt.timedelta(seconds=(end - beg))
    print(prefix + '... processing finished:', i, 'time:',elapsed)


def process_samples(nlp, interesting_verbs, samples):

    stats = collections.Counter()
    docs = nlp.pipe(samples, batch_size=10000, n_process=6)
    items = zip(samples, docs)
    items = log_progress_iterator('nlp', 10000, items)
    for input_text, doc in items:
        events = find_collocations(interesting_verbs, doc)
        stats.update(events)

    stats = list(stats.items())
    print('collocations found:', len(stats))
    # print(stats)

    print('=' * 80)

    def sorting_key(s):
        (verb, adv), n = s
        return (verb, -n, adv)

    def grouping_key(s):
        verb = s[0][0]
        return verb

    stats = sorted(stats, key=sorting_key)
    for verb, group_it in itertools.groupby(stats, grouping_key):
        print()
        verb_stats_text = ', '.join(
            '({}, {})'.format(adv, n)
            for (verb, adv), n in group_it
        )
        print('{}: {}'.format(verb, verb_stats_text))


def main():
    # nlp = spacy.load('en_core_web_sm')
    nlp = spacy.load('en_core_web_md')
    print('Model loaded.')

    INTERESTING_VERBS = (
        'say',
        'tell',
        'speak',
        'claim',
        'communicate',

        'state',
        'pronounce',
        'articulate',
        'talk',
    )

    interesting_verbs = set(INTERESTING_VERBS)

    blog_samples = load_blog_texts()
    # blog_samples = blog_samples[:10000]

    have_word_with_ly_ending_pattern = re.compile(r'ly\b')

    def basic_preprocessing_filter(line):
        search_result = have_word_with_ly_ending_pattern.search(line)
        return search_result is not None

    n = len(blog_samples)
    blog_samples = [s for s in blog_samples if basic_preprocessing_filter(s)]
    nf = len(blog_samples)
    print('before filter:', n)
    print(' after filter:', nf)

    process_samples(nlp, interesting_verbs, blog_samples)


if __name__ == '__main__':
    main()
