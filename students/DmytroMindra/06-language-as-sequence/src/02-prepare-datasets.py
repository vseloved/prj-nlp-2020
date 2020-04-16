import json
from random import random, randrange

import stanza

stanza.download('en')
nlp = stanza.Pipeline('en', processors='tokenize, mwt, pos, lemma, depparse')

RAW_SENTENCES_FILENAME = '../data/raw-data/stripped_masc_sentences.json'
TOKENS_FILENAME = '../data/raw-data/tokens_dataset.json'
LABELS_FILENAME = '../data/raw-data/labels_dataset.json'


def decision(probability):
    return random() < probability


def get_root_distance(word_no, sentence):
    max_distance = 8
    word = sentence.words[word_no]
    distance = 0

    while distance <= max_distance and word.head != 0:
        word = sentence.words[word.head - 1]
        distance += 1

    return distance


def extract_features(sentences):
    labels = []
    tokens = []
    sentence_count = len(sentences)
    current_shift = 0
    sentence_end_positions = []
    text = ''

    for sentence_no in range(sentence_count):
        sentence = sentences[sentence_no];
        if sentence_no != sentence_count - 1:
            if sentence.endswith('.'):
                sentence = sentence[:-1]
            sentence_end_positions.append(current_shift + len(sentence) - 1)
            current_shift += len(sentence)

        if sentence_no > 0:
            lower_case_decision = decision(0.5)
            if lower_case_decision:
                sentence = sentence[:1].lower() + sentence[1:]
        if text == '':
            text = sentence
        else:
            text = text + ' ' + sentence

    doc = nlp(text)
    current_sentnse = 0

    for sentence in doc.sentences:
        for token_no in range(len(sentence.tokens)):
            token = sentence.tokens[token_no]
            word = token.words[0]
            root_distance = get_root_distance(token_no, sentence)
            text = word.text

            if len(text) > 0 and text[0].isupper():
                is_upper = True
            else:
                is_upper = False

            left_token = ''
            left_pos = ''

            right_token = ''
            right_pos = ''
            is_right_upper = False

            if token_no > 0:
                left_token = sentence.tokens[token_no - 1].text
                left_pos = sentence.tokens[token_no - 1].words[0].pos

            if token_no < len(sentence.tokens) - 2:
                right_token = sentence.tokens[token_no + 1].text
                right_pos = sentence.tokens[token_no + 1].words[0].pos

                if len(sentence.tokens[token_no + 1].text) > 0 and \
                        sentence.tokens[token_no + 1].text[0].isupper():
                    is_right_upper = True

            features = {'text': word.text,
                        'pos': word.pos,
                        'lemma': word.lemma,
                        'deprel': word.deprel,
                        'root_distance': root_distance,
                        'is_upper': is_upper,
                        'left_token': left_token,
                        'left_pos': left_pos,
                        'right_token': right_token,
                        'right_pos': right_pos,
                        'is_right_upper': is_right_upper
                        }

            label = False

            if sentence_count > 1 and \
                    current_sentnse < sentence_count - 1 and \
                    token.end_char > sentence_end_positions[current_sentnse]:
                current_sentnse += 1
                label = True

            tokens.append(features)
            labels.append(label)

    return (tokens, labels)


def debug_extract_features():
    text = ["For this event, when you purchase a corporate picnic table, you will be able to bring 16 people.",
            "We must be able to reach all youth and families interested in values - based programs.",
            "I can't imagine not being able to see."]

    doc = nlp(''.join(text))

    for word in doc.sentences[0].words:
        print(word.text, word.pos, word.lemma, word.deprel)

    dataset = extract_features(text)
    labels = dataset[1]
    tokens = dataset[0]

    for i in range(len(labels)):
        print(tokens[i], labels[i])


if __name__ == "__main__":
    debug_extract_features()

    with open(RAW_SENTENCES_FILENAME) as json_file:
        data = json.load(json_file)

    labels = []
    tokens = []

    counter = 0

    while len(data)>0:

        batch_size = randrange(4)+1
        batch = data[:batch_size]
        data = data[batch_size:]
        dataset = extract_features(batch)
        tokens.append(dataset[0])
        labels.append(dataset[1])
        counter += 1
        if counter % 10 == 0:
            print('to go', len(data))

    with open(TOKENS_FILENAME, 'w') as outfile:
        json.dump(tokens, outfile)

    with open(LABELS_FILENAME, 'w') as outfile:
        json.dump(labels, outfile)
