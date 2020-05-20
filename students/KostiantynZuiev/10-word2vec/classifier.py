import json
import pickle
import langid
import re
import string

import spacy
import tokenize_uk
import pymorphy2  
   
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import StackingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer

from gensim.models.doc2vec import Doc2Vec, TaggedDocument


nlp_uk = spacy.load('/home/holdbar/nltk_data/models/uk_vectors')
# nlp_uk = spacy.load('/home/holdbar/nltk_data/models/uk_vectors_uber')
morph = pymorphy2.MorphAnalyzer(lang='uk')

tag_mapping = {"ADJF": "ADJ", "ADJS": "ADJ", "COMP": "ADJ", "PRTF": "ADJ",
           "PRTS": "ADJ", "GRND": "VERB", "NUMR": "NUM", "ADVB": "ADV",
           "NPRO": "PRON", "PRED": "ADV", "PREP": "ADP", "PRCL": "PART"}

with open('dataset.json', 'r') as f:
    dataset = json.load(f)
    
def vectorize(words):
    v = nlp_uk('unk')[0].vector
    for w in words:
        v += nlp_uk(w)[0].vector
        v /= len(words)

    return v

def lemmatize_tokens(tokens):
    words_lemmas = []
    for t in tokens:
        words_lemmas.append(
            morph.parse(t)[0].normal_form
        )

    return words_lemmas

def filter_words_with_pos(tokens, useful_tags):
    filtered_words = []
    for t in tokens:
        tag = morph.parse(t)[0].tag.POS
        if tag_mapping.get(tag, str(tag)) in useful_tags:
            filtered_words.append(t)

    return filtered_words


### Preprocessing

tokenized_data = []
for item in dataset:
    sents_list = []
    sents = tokenize_uk.tokenize_sents(item[1])
    for s in sents:
        sents_list.append(tokenize_uk.tokenize_words(s))
    tokenized_data.append(sents_list)

tokenized_lengths = [len(t) for t in tokenized_data]
print("tokenized")
lemmatized_data = [[lemmatize_tokens(i) for i in t] for t in tokenized_data]
print("lemmatized")
digits_cleared_data = [[[item for item in i if not item.isdigit()] for i in l] for l in lemmatized_data]
print("digits")
punct_cleared_data = [[[item for item in i if item not in f'{string.punctuation}”№«»'] for i in d] for d in digits_cleared_data]
print("punct")
print(punct_cleared_data[0])
pos_filtered_data = [[filter_words_with_pos(i, ["NOUN", "VERB", "ADJ", "ADV"]) for i in p] for p in punct_cleared_data]
print("pos")
print(len(tokenized_data))
with open(f'preprocessed_dataset.pickle', 'wb') as f:
    pickle.dump(pos_filtered_data, f)

labels = [i[0] for i in dataset]

with open(f'preprocessed_dataset.pickle', 'rb') as f:
    pos_filtered_data = pickle.load(f)

print(pos_filtered_data[0])

### basic
print("############### KNN basic:")

data = [vectorize(i) for i in tokenized_data]

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=42)


knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
                     metric_params=None, n_jobs=None, n_neighbors=3, p=2,
                     weights='uniform')

knn.fit(X_train, y_train)

print(classification_report(y_test, knn.predict(X_test)))

### lemmatization
print("############# KNN lemmatized:")

data = [vectorize(i) for i in lemmatized_data]

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=42)


knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
                     metric_params=None, n_jobs=None, n_neighbors=3, p=2,
                     weights='uniform')

knn.fit(X_train, y_train)

print(classification_report(y_test, knn.predict(X_test)))

#### digits clear
print("########### KNN digits cleared:")

data = [vectorize(i) for i in digits_cleared_data]

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=42)


knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
                     metric_params=None, n_jobs=None, n_neighbors=3, p=2,
                     weights='uniform')

knn.fit(X_train, y_train)

print(classification_report(y_test, knn.predict(X_test)))


#### punct clear
print("############# KNN punct cleared:")

data = [vectorize(i) for i in punct_cleared_data]

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=42)


knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
                     metric_params=None, n_jobs=None, n_neighbors=3, p=2,
                     weights='uniform')

knn.fit(X_train, y_train)

print(classification_report(y_test, knn.predict(X_test)))


#### pos filtered
print("############## KNN POS filtered:")


data = [vectorize(i) for i in pos_filtered_data]

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=42)


knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
                     metric_params=None, n_jobs=None, n_neighbors=3, p=2,
                     weights='uniform')

knn.fit(X_train, y_train)

print(classification_report(y_test, knn.predict(X_test)))


#### tfidf vectors
print("############## KNN tf-idf:")

vectorizer = TfidfVectorizer()

data = vectorizer.fit_transform([" ".join(i) for i in pos_filtered_data])

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=42)


knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
                     metric_params=None, n_jobs=None, n_neighbors=10, p=2,
                     weights='uniform')

knn.fit(X_train, y_train)

print(classification_report(y_test, knn.predict(X_test)))


#### tfidf vectors on random forest classifier
print("############## RFC tf-idf:")

vectorizer = TfidfVectorizer()

data = vectorizer.fit_transform([" ".join(i) for i in pos_filtered_data])

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=42)


svc = SVC(kernel='sigmoid')

svc.fit(X_train, y_train)

print(classification_report(y_test, svc.predict(X_test)))

#### classifiers ensemble(knn+svc) with tf-idf vectors

estimators = [
    ('knn', KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
                      metric_params=None, n_jobs=None, n_neighbors=10, p=2,
                      weights='uniform')),
   # ('svc', SVC(kernel='sigmoid'))
    ('lrc', LogisticRegression())
]

clf = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression())

vectorizer = TfidfVectorizer()

print([[" ".join(i) for i in p] for p in pos_filtered_data][0])

data = vectorizer.fit_transform([" ".join([" ".join(i) for i in p]) for p in pos_filtered_data])


X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=42)


clf.fit(X_train, y_train)

print(classification_report(y_test, clf.predict(X_test)))

# #### doc2vec with KNN

# print(pos_filtered_data[0])

# glued_data = []
# for item in pos_filtered_data:
#     new_item = []
#     for sent in item:
#         new_item.append(" ".join(sent))
#     glued_data.append(". ".join(new_item))

# print(glued_data[0])

# documents = [TaggedDocument(doc[1], [i]) for i, doc in enumerate(glued_data)]



# model = Doc2Vec(documents, vector_size=30, window=2, min_count=1, workers=4)
# model.train(documents, total_examples=len(glued_data), epochs=300)

# vectors = [model.infer_vector([p]) for p in glued_data]

# # vectors = []
# # for i, _ in enumerate(glued_data):
# #     vectors.append(model.docvecs[i])

# X_train, X_test, y_train, y_test = train_test_split(vectors, labels, test_size=0.33, random_state=42)


# knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
#                     metric_params=None, n_jobs=None, n_neighbors=10, p=2,
#                     weights='uniform')

# knn.fit(X_train, y_train)

# print(classification_report(y_test, knn.predict(X_test)))
