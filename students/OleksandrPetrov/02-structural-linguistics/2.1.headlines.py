#!/usr/bin/env python

import os
import io
import json

import spacy

HERE = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(HERE, '..', '..', '..', 'tasks', '02-structural-linguistics', 'data')


def identity(text):
    yield text


def first_letter_to_upper(text):
    yield text[:1].upper()
    yield text[1:]


def first_letter_to_lower(text):
    yield text[:1].lower()
    yield text[1:]


def format_as_headline(doc):

    transforms = {}

    def set_transform(pos, transform_fn):
        # do not allow transform override
        if pos not in transforms:
            transforms[pos] = transform_fn

    def is_word_candidate(token):
        return not (token.is_punct or token.is_digit or token.is_space or token.is_bracket or token.is_quote or token.is_currency)

    word_lens = {}
    n = len(doc)
    first_word_pos = None
    last_word_pos = None
    for i in range(n):
        token = doc[i]
        if not is_word_candidate(token):
            set_transform(i, identity)
            continue
        if first_word_pos is None:
            first_word_pos = i
        last_word_pos = i
        word_lens[i] = len(token.text)

    # Rule 1

    for pos, word_len in word_lens.items():
        if word_len >= 4:
            set_transform(pos, first_letter_to_upper)

    # Rule 2

    set_transform(first_word_pos, first_letter_to_upper)
    set_transform(last_word_pos, first_letter_to_upper)

    # Rule 3

    for i in range(n):
        token = doc[i]
        if token.pos_ in ('NOUN', 'PRON', 'VERB', 'AUX', 'ADJ', 'ADV'):
            # print(token.text, token.pos_, '=> upper')
            set_transform(i, first_letter_to_upper)

    # Rule 4

    hyphenated_words_groups = []
    hyphenated_word_positions = []

    BREAK = 'break'
    WORD = 'word'
    HYPHEN = 'hyphen'

    prev_token_type = BREAK
    curr_token_type = None

    for i in range(n):
        token = doc[i]

        curr_has_traling_whitespace = len(token.whitespace_) > 0 or (i == (n - 1))

        if token.text == '-':
            curr_token_type = HYPHEN
        elif is_word_candidate(token):
            curr_token_type = WORD
        else:
            curr_token_type = BREAK

        if prev_token_type == BREAK and curr_token_type == WORD:
            hyphenated_word_positions.append(i)
        elif prev_token_type == HYPHEN and curr_token_type == WORD:
            hyphenated_word_positions.append(i)

        need_to_break = curr_token_type == BREAK or curr_has_traling_whitespace
        if need_to_break:
            if len(hyphenated_word_positions) > 1:
                hyphenated_words_groups.append(tuple(hyphenated_word_positions))
            hyphenated_word_positions = []
            curr_token_type = BREAK

        prev_token_type = curr_token_type

    for pos_group in hyphenated_words_groups:
        for pos in pos_group:
            # print('hyphen:', [doc[k] for k in range(min(pos_group), max(pos_group)+1)])
            set_transform(pos, first_letter_to_upper)

    # Rule 5

    for i in range(n):
        token = doc[i]
        if token.pos_ in ('DET', 'CONJ', 'ADP', 'PART', 'INTJ'):
            # print(token.text, token.pos_, '=> lower')
            set_transform(i, first_letter_to_lower)

    # ===========================

    for pos in range(n):
        set_transform(pos, identity)

    def generate_fragments_applying_transforms(transforms, doc):
        n = len(doc)
        for i in range(n):
            token = doc[i]
            transform_fn = transforms[i]
            for fragment in transform_fn(token.text):
                yield fragment
            yield token.whitespace_

    result = ''.join(generate_fragments_applying_transforms(transforms, doc))
    return result


def load_validation_texts():
    data_file_path = os.path.join(DATA_DIR, 'headlines-test-set.json')
    with io.open(data_file_path, 'rt', encoding='utf-8') as text_istream:
        data = json.load(text_istream)
    return [
        (input_text, expected_result)
        for input_text, expected_result in data
    ]


def load_examiner_texts():
    data_file_path = os.path.join(DATA_DIR, 'examiner-headlines.txt')
    with io.open(data_file_path, 'rt', encoding='utf-8') as text_istream:
        samples = []
        for line in text_istream:
            line = line.strip()
            input_text, expected_result = line, line
            samples.append((input_text, expected_result))
        return samples


def process_samples(nlp, samples):

    def input_texts_iter(samples):
        for input_text, __ in samples:
            yield input_text

    total = len(samples)
    errors = 0
    docs = nlp.pipe(input_texts_iter(samples))
    for (input_text, expected_result), doc in zip(samples, docs):
        headline = format_as_headline(doc)
        if headline != expected_result and '-' in expected_result:
            errors += 1
            print('   Input:', input_text)
            print('  Output:', headline)
            print('Expected:', expected_result)
            print()
    print('Total samples: {}, Errors: {}, Success ratio: {}'.format(total, errors, (total-errors)/total))


def main():
    nlp = spacy.load('en_core_web_sm')
    # nlp = spacy.load('en_core_web_md')

    my_samples = [
        (
            "You don't stop me now.",
            "You Don't Stop me now.",
        ),
        (
            "Do as you want",
            "Do As You Want",
        ),
        (
            "How to use a Macbook as a table",
            "How to Use a Macbook as a Table",
        ),
    ]
    validation_samples = load_validation_texts()
    examiner_samples = load_examiner_texts()

    # process_samples(nlp, my_samples)
    process_samples(nlp, validation_samples)
    # process_samples(nlp, examiner_samples)


if __name__ == '__main__':
    main()
