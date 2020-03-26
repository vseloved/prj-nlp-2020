import en_core_web_md
import json
import os

absDir = os.path.dirname(os.path.abspath(__file__))
data_dir = '../../../../tasks/02-structural-linguistics/data/'
tasksDir = os.path.join(absDir, data_dir)
HEADLINES_TEST_FILE = os.path.join(tasksDir, 'headlines-test-set.json')
EXAMINER_HEADLINES_FILE = os.path.join(tasksDir, 'examiner-headlines.txt')

nlp = en_core_web_md.load()

with open(HEADLINES_TEST_FILE, 'r') as f:
    data = json.load(f)
with open(EXAMINER_HEADLINES_FILE, 'r') as f:
    corpus = f.readlines()


def headline(doc):
    res = ''

    valid_pos = ['NOUN', 'VERB', 'AUX', 'PRON', 'ADJ', 'ADV', 'SCONJ']
    invalid_pos = ['DET', 'CONJ', 'CCONJ', 'PART', 'INTJ', 'ADP']

    sent_len = len(doc) - 1

    for token in doc:
        prev_token = doc[token.i - 1]
        next_token = doc[token.i + 1] if sent_len > token.i else None

        is_part_of_hyphened = prev_token.text == '-' \
            and not prev_token.whitespace_ \
            or next_token and next_token.text == '-' \
            and not next_token.whitespace_
        is_start_of_quote = prev_token.is_quote and not prev_token.whitespace_
        is_last = token.i == sent_len or token.i == sent_len - \
            1 and doc[sent_len].is_punct
        is_adp = token.pos_ == 'SCONJ' and \
            any(c.pos_ == 'NOUN' or c.pos_ == 'ADP' or c.pos_ ==
                'PROPN' for c in token.children)
        is_pron = token.lemma_ == '-PRON-' or token.pos_ == 'DET' \
            and token.head.pos_ == 'PRON'
        is_det_title = token.pos_ == 'DET' and prev_token.pos_ == 'PUNCT'
        is_propn_to_capitalize = len(
            token.text) <= 3 and token.pos_ == 'PROPN' and token.is_lower
        is_propn_to_skip = token.pos_ == 'PROPN' and not token.is_lower
        is_neg_adv = token.text.lower() == 'not' and \
            (token.head.pos_ == 'AUX' or token.head.pos_ ==
             'VERB' or token.head.pos_ == 'ADJ')

        should_capitalize = (
            len(token.text) > 3
            or ((token.is_sent_start or is_last)
                and not token.is_punct and not token.is_quote
                ) or is_part_of_hyphened
            or is_start_of_quote
            or token.pos_ in valid_pos
            or is_pron or is_det_title
            or is_propn_to_capitalize
            or is_neg_adv
        ) and not token.is_upper and not (len(token.text) <= 3 and is_adp) \
            and not is_propn_to_skip

        if should_capitalize:
            res += token.text.capitalize()
        elif token.pos_ in invalid_pos:
            res += token.text.lower()
        else:
            res += token.text
        res += token.whitespace_

    return res


def accuracy(data):
    ok = 0

    for inp, exp in data:
        doc = nlp(inp)
        if (headline(doc) == exp):
            ok += 1

    return ok/len(data)


def test_corpus(corpus):
    ok = 0
    for line in corpus:
        formatted = headline(nlp(line))
        if formatted == line:
            ok += 1
    return ok, ok/len(corpus)


# main
accuracy(data)
test_corpus(corpus)
