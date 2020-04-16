import json
from random import random

import stanza

stanza.download('en')
nlp = stanza.Pipeline('en')

RAW_SENTENCES_FILENAME = '../data/raw-data/stripped_masc_sentences.json'
TOKENS_FILENAME = '../data/raw-data/tokens_dataset.json'
LABELS_FILENAME = '../data/raw-data/labels_dataset.json'

def decision(probability):
    return random() < probability

def extract_features(text, generate_error):
    labels = []
    tokens = []
    doc = nlp(text)

    for sentence in doc.sentences:
        for word_no in range(len(sentence.words)):
            word = sentence.words[word_no]
            token = {'text': word.text, 'pos': word.pos, 'lemma': word.lemma, 'deprel': word.deprel}

            label = False

            if generate_error and word_no == len(sentence.words) - 2:
                label = True

            if generate_error and word_no == len(sentence.words) - 1:
                pass
            else:
                tokens.append(token)
                labels.append(label)

    return (tokens, labels)


def debug_extract_features():
    text = "For this event, when you purchase a corporate picnic table, you will be able to bring 16 people."
    doc = nlp(text)

    for word in doc.sentences[0].words:
        print(word.text, word.pos, word.lemma, word.deprel)

    dataset = extract_features(text,False)
    labels = dataset[1]
    tokens = dataset[0]

    for i in range(len(labels)):
        print(tokens[i], labels[i])


if __name__ == "__main__":

    with open(RAW_SENTENCES_FILENAME) as json_file:
        data = json.load(json_file)

    labels = []
    tokens = []

    counter = 0
    for sentence in data:
        dataset = extract_features(sentence, decision(0.5))
        tokens.append(dataset[0])
        labels.append(dataset[1])
        counter += 1
        if counter % 100 == 0:
            print(counter, len(data))

    with open(TOKENS_FILENAME, 'w') as outfile:
        json.dump(tokens, outfile)

    with open(LABELS_FILENAME, 'w') as outfile:
        json.dump(labels, outfile)