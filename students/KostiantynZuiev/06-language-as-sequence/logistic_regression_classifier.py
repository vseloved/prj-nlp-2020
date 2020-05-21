import json
import nltk
import functools
from collections import Counter
from nltk.stem import WordNetLemmatizer 
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.metrics import classification_report

lemmatizer = WordNetLemmatizer() 

# with open('run_on_dataset_brown.json','r') as f:
#     dataset = json.load(f)

with open('run_on_dataset_brown.json','r') as f:
    dataset = json.load(f)

with open('prepared-tailing-5-grams.json','r') as f:
    ngrams = json.load(f)

def get_word_context(index, tokens):
    features = dict()
    features['w'] = tokens[index][0]

    return features

def get_neighbor_word_context(index, tokens):
    features = dict()
    features['w-2'] = tokens[index-2][0] if index >= 2 else '<S>'
    features['w-1'] = tokens[index-1][0] if index >= 1 else '<S>'
    features['w+1'] = tokens[index+1][0] if index <= len(tokens) - 2 else '</S>'
    features['w+2'] = tokens[index+2][0] if index <= len(tokens) - 3 else '</S>'

    return features

def get_pos_context(index, tokens):
    features = dict()
    features['p-2'] = tokens[index-2][2] if index >= 2 else '<P>'
    features['p-1'] = tokens[index-1][2] if index >= 1 else '<P>'
    features['p'] = tokens[index][2]
    features['p+1'] = tokens[index+1][2] if index <= len(tokens) - 2 else '</P>'
    features['p+2'] = tokens[index+2][2] if index <= len(tokens) - 3 else '</P>'

    return features

def get_case_context(index, tokens):
    features = dict()
    features['c-2'] = get_case_label(tokens[index-2][0]) if index >= 2 else '<C>'
    features['c-1'] = get_case_label(tokens[index-1][0]) if index >= 1 else '<C>'
    features['c'] = get_case_label(tokens[index][0])
    features['c+1'] = get_case_label(tokens[index+1][0]) if index <= len(tokens) - 2 else '</C>'
    features['c+2'] = get_case_label(tokens[index+2][0]) if index <= len(tokens) - 3 else '</C>'

    return features

def get_lemma_context(index, tokens):
    features = dict()
    features['l-2'] = tokens[index-2][3] if index >= 2 else '<L>'
    features['l-1'] = tokens[index-1][3] if index >= 1 else '<L>'
    features['l'] = tokens[index][3]
    features['l+1'] = tokens[index+1][3] if index <= len(tokens) - 2 else '</L>'
    features['l+2'] = tokens[index+2][3] if index <= len(tokens) - 3 else '</L>'

    return features

def get_case_label(text):
    if text.isupper():

        return 'is_upper'
    elif text[0].isupper():

        return 'is_capital'
    elif text.islower():

        return 'is_lower'
    else:
        
        return 'O'

def get_ngram_context(index, tokens):
    features = dict()
    pre_token = tokens[index-1][0] if index >= 1 else None
    token = tokens[index][0]
    if token and pre_token:
        if (pre_token, token) in ngrams:
            features['n-1'] = 'pre_pre_period'
            features['n'] = 'pre_period'

            return features
        features['n-1'] = 'no_ngram'

    features['n'] = 'no_ngram'

    return features


def get_all_features(tokens, extraction_functions):
    all_features = []
    for i in range(len(tokens)):
        print(i, end="\r", flush=True)
        token_features = dict()
        for ef in extraction_functions:
            token_features.update(ef(i,tokens))
        all_features.append(token_features)
    
    return all_features

def prepare_dataset(dataset):
    print(len(dataset))
    prepared_dataset = []
    for item in dataset:
        tokens = [t[0] for t in item]
        labels = [t[1] for t in item]
        pos_tokens = [p[1] for p in nltk.pos_tag(tokens)]
        lemma_tokens = [lemmatizer.lemmatize(t) for t in tokens]
        prepared_dataset.append(list(
            zip(tokens,labels,pos_tokens,lemma_tokens)
        ))
    print(len(prepared_dataset))
    return prepared_dataset





prepared_dataset = prepare_dataset(dataset)
print('prepared dataset')

train_dataset, test_dataset = prepared_dataset[:round(0.8*len(prepared_dataset))], prepared_dataset[round(0.8*len(prepared_dataset)):]

X_train_tokens = [item for sentence in train_dataset for item in sentence]
y_train_labels = [item[1] for sentence in train_dataset for item in sentence]

X_test_tokens = [item for sentence in test_dataset for item in sentence]
y_test_labels = [item[1] for sentence in test_dataset for item in sentence]


log_res = LogisticRegression(random_state=42, multi_class='multinomial',
                         solver='sag', max_iter=300)

# with word context only
features_extractors = [get_word_context]
dict_vec = DictVectorizer()
all_train_features = get_all_features(X_train_tokens, features_extractors)
print('got train features')
vectorized_features = dict_vec.fit_transform(all_train_features)
log_res.fit(vectorized_features, y_train_labels)
all_test_features = get_all_features(X_test_tokens, features_extractors)
print('start prediction')
print("single word:")
print(classification_report(y_test_labels, log_res.predict(dict_vec.transform(all_test_features))))


# add neighbor word context
dict_vec = DictVectorizer()
features_extractors.append(get_neighbor_word_context)
all_train_features = get_all_features(X_train_tokens, features_extractors)
print('got train features')
vectorized_features = dict_vec.fit_transform(all_train_features)
log_res.fit(vectorized_features, y_train_labels)
all_test_features = get_all_features(X_test_tokens, features_extractors)
print('start prediction')
print("+neighbors:")
print(classification_report(y_test_labels, log_res.predict(dict_vec.transform(all_test_features))))


# add case context
dict_vec = DictVectorizer()
features_extractors.append(get_case_context)
all_train_features = get_all_features(X_train_tokens, features_extractors)
print('got train features')
vectorized_features = dict_vec.fit_transform(all_train_features)
log_res.fit(vectorized_features, y_train_labels)
all_test_features = get_all_features(X_test_tokens, features_extractors)
print('start prediction')
print("+case:")
print(classification_report(y_test_labels, log_res.predict(dict_vec.transform(all_test_features))))


# add lemma context
dict_vec = DictVectorizer()
features_extractors.append(get_lemma_context)
all_train_features = get_all_features(X_train_tokens, features_extractors)
print('got train features')
vectorized_features = dict_vec.fit_transform(all_train_features)
log_res.fit(vectorized_features, y_train_labels)
all_test_features = get_all_features(X_test_tokens, features_extractors)
print('start prediction')
print("+lemma:")
print(classification_report(y_test_labels, log_res.predict(dict_vec.transform(all_test_features))))


# add POS context
dict_vec = DictVectorizer()
features_extractors.append(get_pos_context)
all_train_features = get_all_features(X_train_tokens, features_extractors)
print('got train features')
vectorized_features = dict_vec.fit_transform(all_train_features)
log_res.fit(vectorized_features, y_train_labels)
all_test_features = get_all_features(X_test_tokens, features_extractors)
print('start prediction')
print("+POS:")
print(classification_report(y_test_labels, log_res.predict(dict_vec.transform(all_test_features))))


# add ngram context
dict_vec = DictVectorizer()
features_extractors.append(get_ngram_context)
all_train_features = get_all_features(X_train_tokens, features_extractors)
print('got train features')
vectorized_features = dict_vec.fit_transform(all_train_features)
log_res.fit(vectorized_features, y_train_labels)
all_test_features = get_all_features(X_test_tokens, features_extractors)
print('start prediction')
print("+N-gram:")
print(classification_report(y_test_labels, log_res.predict(dict_vec.transform(all_test_features))))


with open('run-on-test.json','r') as f:
    test_dataset = json.load(f)


prepared_test_dataset = prepare_dataset(test_dataset)
print('prepared dataset')

test_tokens = [item for sentence in prepared_test_dataset for item in sentence]
test_labels = [item[1] for sentence in prepared_test_dataset for item in sentence]
all_test_features = get_all_features(test_tokens, features_extractors)
print('start prediction')
print("TEST DATASET:")
print(classification_report(test_labels, log_res.predict(dict_vec.transform(all_test_features))))