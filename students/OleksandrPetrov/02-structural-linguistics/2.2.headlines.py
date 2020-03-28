#!/usr/bin/env python

import os
import io
import collections

import spacy
from spacy_wordnet import wordnet_annotator
from nltk.corpus import sentiwordnet
import matplotlib.pyplot as plt

HERE = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(HERE, '..', '..', '..', 'tasks', '02-structural-linguistics', 'data')

SYNSET_POS = {
    'NOUN': 'n',
    'VERB': 'v',
    'ADJ': 'j',
    'ADV': 'r',
}


def analyze_headline(doc):

    prominence = 0
    for name in doc.ents:
        if name.label_ in ('PERSON', 'ORG'):
            # print('prominence:', name.text)
            prominence += 1

    def match_synset(pos, lemma, synset):
        if SYNSET_POS[pos] != synset.pos():
            return False
        if lemma not in set(synset.lemma_names()):
            return False
        return True

    def average_score(scores):
        n = len(scores)
        return (
            sum(s[0] for s in scores) / n,
            sum(s[1] for s in scores) / n,
            sum(s[2] for s in scores) / n,
        )

    sentiments = []
    for token in doc:
        if token.pos_ not in ('NOUN', 'VERB', 'ADJ', 'ADV'):
            continue
        synsets = token._.wordnet.synsets()
        synsets = [s for s in synsets if match_synset(token.pos_, token.lemma_, s)]
        sentis = [sentiwordnet.senti_synset(s.name()) for s in synsets]
        scores = [
            (s.pos_score(), s.obj_score(), s.neg_score())
            for s in sentis
        ]
        if scores:
            sentiments.append(average_score(scores))

    superlativeness = 0
    for token in doc:
        if token.pos_ == 'ADJ':
            if token.tag_ in ('JJR', 'JJS'):
                # print('superlativeness:', token.text)
                superlativeness += 1
        if token.pos_ == 'ADV':
            if token.tag_ in ('RBR', 'RBS'):
                # print('superlativeness:', token.text)
                superlativeness += 1

    def aggregate_sentiments(sentiments):
        result = 0
        for pos, obj, neg in sentiments:
            # a) pos + obj + neg == 1
            # b) we are interested only in degree in of emotion
            # c) more emotional words => more emotional degree => let it be additive
            result += pos + neg
        return result

    sentiment = aggregate_sentiments(sentiments)

    return (prominence, sentiment, superlativeness)


def load_examiner_texts():
    data_file_path = os.path.join(DATA_DIR, 'examiner-headlines.txt')
    with io.open(data_file_path, 'rt', encoding='utf-8') as text_istream:
        samples = []
        for line in text_istream:
            input_text = line.strip()
            samples.append(input_text)
        return samples


def prominence_classifier(v):
    return v > 0


def superlativeness_classifier(v):
    return v > 0


def sentiment_classifier(v):
    return v >= 0.5  # some rather arbitrary estimation from histogram


def process_samples(nlp, samples):

    prominence_items = []
    sentiment_items = []
    superlativeness_items = []

    print('starting...')
    total = len(samples)
    docs = nlp.pipe(samples)
    for (n, input_text), doc in zip(enumerate(samples), docs):
        prominence, sentiment, superlativeness = analyze_headline(doc)
        prominence_items.append(prominence)
        sentiment_items.append(sentiment)
        superlativeness_items.append(superlativeness)
        if (n + 1) % 1000 == 0:
            print('processed:', n + 1)
    print('finished.')

    def print_ratio(name, classifier_fn, items):
        n = len(items)
        nc = sum(1 for __ in filter(classifier_fn, items))
        print('{}: {} from {}, ratio: {}'.format(name, nc, n, nc / n))

    print('=' * 80)

    print_ratio('prominent', prominence_classifier, prominence_items)
    print_ratio('sentiment', sentiment_classifier, sentiment_items)
    print_ratio('superlativeness', superlativeness_classifier, superlativeness_items)

    print('=' * 80)

    prominence_stats = collections.Counter(prominence_items)
    print('prominence_stats:', prominence_stats)
    plt.figure()
    plt.hist(prominence_items, bins=len(prominence_stats))
    plt.savefig('2.2.prominence.hist.png')

    superlativeness_stats = collections.Counter(superlativeness_items)
    print('superlativeness_stats:', superlativeness_stats)
    plt.figure()
    plt.hist(superlativeness_items, bins=len(superlativeness_stats))
    plt.savefig('2.2.superlativeness.hist.png')

    sentiment_items_all = sentiment_items
    sentiment_items_classified = list(filter(sentiment_classifier, sentiment_items))
    plt.figure()
    plt.hist(sentiment_items_all, bins=16)
    plt.savefig('2.2.sentiment.hist.all.png')
    plt.figure()
    plt.hist(sentiment_items_classified, bins=16)
    plt.savefig('2.2.sentiment.hist.classified.png')


def main():
    # nlp = spacy.load('en_core_web_sm')
    nlp = spacy.load('en_core_web_md')
    nlp.add_pipe(wordnet_annotator.WordnetAnnotator(nlp.lang), after='tagger')

    my_samples = [
        "You don't stop me now.",
        "Do as you want",
        "How to use a Macbook as a table",
        "Mr. Best flew to New York on Saturday morning.",
        "The old French bridge",
        "The older French bridge",
        "The oldest French bridge",
        "The most beatiful women",
        "He drived more slowly than usually",
    ]

    examiner_samples = load_examiner_texts()
    # examiner_samples = examiner_samples[:100]

    # process_samples(nlp, my_samples)
    process_samples(nlp, examiner_samples)


if __name__ == '__main__':
    main()
