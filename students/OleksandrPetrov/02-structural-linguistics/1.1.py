#!/usr/bin/env python

import nltk

SAMPLES_EN = """
truth, truthful, truthfulness, countertruth, untruthful, truthology

flaw, flaws, flawed, flawless, flawlessness, flawlessly

untouchables

foxes
higher
smelling
happiness
"""

SAMPLES_RU = """
лес, лесной, лесник, лесничий, лесничество, пролесье

окно, окошко, подоконник, оконный, окнище

безоблачный
"""


def main():

    stemmer_en = nltk.stem.SnowballStemmer('english').stem
    stemmer_ru = nltk.stem.SnowballStemmer('russian').stem

    def to_words(text):
        text = text.replace(',', ' ')
        tokens = text.split()
        tokens = [t.strip() for t in tokens]
        words = [t for t in tokens if t]
        return words

    def do_stemming(stem_fn, words):
        return [(word, stem_fn(word)) for word in words]

    def print_result(r):
        for w, sw in r:
            print(w, '=>', sw)

    print_result(
        do_stemming(stemmer_en, to_words(SAMPLES_EN))
    )

    print_result(
        do_stemming(stemmer_ru, to_words(SAMPLES_RU))
    )


if __name__ == '__main__':
    main()
