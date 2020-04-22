import pandas as pd
import pymorphy2


from nltk.tokenize import word_tokenize
from collections import Counter
from copy import deepcopy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from sklearn import svm

morph = pymorphy2.MorphAnalyzer(lang="uk")

df = pd.read_csv('reviews.csv')

ton_df = pd.read_csv('tone-dict-uk.tsv',sep="\t",names=["word", "tone"])

dataset = []

tone_dict = {row['word']:row['tone'] for i,row in ton_df.iterrows()}

def get_review_and_type(review_dict):
    mark = review_dict['mark']
    dignity = review_dict['dignity'] if review_dict['dignity'] != 'nan' else ''
    shortcomings = review_dict['shortcomings'] if review_dict['shortcomings'] != 'nan' else ''
    text = review_dict['text']
    if "?" in text:

        return '', '', '', ''
    if mark in [4, 5]:

        return "pos", text, dignity, shortcomings
    if mark in [1, 2, 3]:

        return "neg", text, dignity, shortcomings

    if dignity and not shortcomings:

        return "pos", text, dignity, shortcomings
    if shortcomings and not dignity:

        return "neg", text, dignity, shortcomings

    return "neut", text, dignity, shortcomings


def check_text_with_tone_dict(text):
    for token in str(text).split():
        if tone_dict.get(token, 0) != 0:

            return tone_dict[token]
  
    return 0

def get_type_with_tone_dict(review_type, review_text, review_dignity, review_shortcomings):
    if any([
        check_text_with_tone_dict(review_text) < 0,
        check_text_with_tone_dict(review_shortcomings) < 0
    ]):
        review_type = "neg"
    if any([
        check_text_with_tone_dict(review_text) > 0,
        check_text_with_tone_dict(review_dignity) > 0
    ]):
        review_type = "pos"
    
    return review_type, review_text, review_dignity, review_shortcomings

def clean_text(text):
    text = text.replace('<br />\n', ' ')

    return text

def get_lemmatized_text(text):
    tokens = word_tokenize(text)
    
    return " ".join([morph.parse(t)[0].normal_form for t in tokens])



# basic version
print("Basic version:\n")
for i, row in df.iterrows():
    row['text'] = clean_text(row['text'])
    review_type, review_text, _, _ = get_review_and_type(row)
    if review_type:
        dataset.append((review_type, review_text))


matrix = CountVectorizer()
X = matrix.fit_transform([d[1] for d in dataset]).toarray()

y = [d[0] for d in dataset]

c = Counter(y)

print(c)

X_train, X_test, y_train, y_test = train_test_split(X, y)


classifier = GaussianNB()
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)


report = metrics.classification_report(y_test, y_pred)

print(report)

basic_y = deepcopy(y_train)

# add lemmatization
print("Lemmatized version:\n")
dataset = []

for i, row in df.iterrows():
    row['text'] = get_lemmatized_text(clean_text(row['text']))
    review_type, review_text, _, _ = get_review_and_type(row)
    if review_type:
        dataset.append((review_type, review_text))


matrix = CountVectorizer()
X = matrix.fit_transform([d[1] for d in dataset]).toarray()

y = [d[0] for d in dataset]

c = Counter(y)

print(c)

X_train, X_test, y_train, y_test = train_test_split(X, y)
 

classifier = GaussianNB()

scores = cross_val_score(classifier, X_train, basic_y, cv=5, scoring='f1_macro')
print("Cross-validation lemmatization to basic: ",scores)

classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)


report = metrics.classification_report(y_test, y_pred)

print(report)

lemma_y = deepcopy(y_train)

# add tone dict check
print("With tone dict:\n")
dataset = []

for i, row in df.iterrows():
    row['text'] = get_lemmatized_text(clean_text(row['text']))
    review_type, review_text, _, _ = get_type_with_tone_dict(*get_review_and_type(row))
    if review_type:
        dataset.append((review_type, review_text))


matrix = CountVectorizer()
X = matrix.fit_transform([d[1] for d in dataset]).toarray()

y = [d[0] for d in dataset]

c = Counter(y)

print(c)

X_train, X_test, y_train, y_test = train_test_split(X, y)
 

classifier = GaussianNB()


scores = cross_val_score(classifier, X_train, lemma_y, cv=5, scoring='f1_macro')
print("Cross-validation tone dict to lemmatization: ",scores)


classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)


report = metrics.classification_report(y_test, y_pred)

print(report)

tone_y = deepcopy(y_train)

# add bigrams
print("With bigrams:\n")
dataset = []

for i, row in df.iterrows():
    row['text'] = get_lemmatized_text(clean_text(row['text']))
    review_type, review_text, _, _ = get_type_with_tone_dict(*get_review_and_type(row))
    if review_type:
        dataset.append((review_type, review_text))

matrix = CountVectorizer(ngram_range=(2,2))
X = matrix.fit_transform([d[1] for d in dataset]).toarray()

y = [d[0] for d in dataset]

c = Counter(y)

print(c)

X_train, X_test, y_train, y_test = train_test_split(X, y)
 

classifier = GaussianNB()


scores = cross_val_score(classifier, X_train, tone_y, cv=5, scoring='f1_macro')
print("Cross-validation bigrams to tone dict: ",scores)


classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)


report = metrics.classification_report(y_test, y_pred)

print(report)