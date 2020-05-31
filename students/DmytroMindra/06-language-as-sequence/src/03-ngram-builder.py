import json
import spacy
nlp = spacy.load("en_core_web_sm")


RAW_SENTENCES_FILENAME = '../data/raw-data/stripped_masc_sentences.json'
NGRAMS_FILENAME = '../data/ngrams.json'

def ngram_collector(tokens):
    ngrams = {}
    count = 0
    for tokenNo in range(1,len(tokens)-2):

        left_token = tokens[tokenNo-1].lower()
        right_token = tokens[tokenNo+1].lower()
        text = tokens[tokenNo].lower()

        if right_token != '<s>' and left_token !='<s>':
            continue

        if right_token == '<s>':
            if text in  ['.',';','...','!',')','?']:
                text = left_token
            if text not in ngrams:
                ngrams[text] = 0
                count +=1
            ngrams[text] += 1

        if left_token == '<s>':
            if '<S>' not in ngrams:
                ngrams['<S>'] = {}
            if text not in ngrams['<S>']:
                ngrams['<S>'][text] = 0
                count +=1
            ngrams['<S>'][text]+=1
    print (count)
    return ngrams

def process_data(data):

    tokens = []
    count = 0
    for text in data:
        count += 1
        if count%100 ==0:
            print (count, len(data))
        doc = nlp(text,disable=["tagger", "parser", "ner"])
        tokens.append('<S>')
        for token in doc:
            tokens.append(token.text.lower())

    tokens.append('<S>')

    return ngram_collector(tokens)


if __name__ == "__main__":


    with open(RAW_SENTENCES_FILENAME) as json_file:
        data = json.load(json_file)

    # local_data = ['Jules Verne is said to have been inspired by a visit here to write Journey to the Center of the Earth.']
    ngrams = process_data(data)

    with open(NGRAMS_FILENAME, 'w') as outfile:
        json.dump(ngrams, outfile)