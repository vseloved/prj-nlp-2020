import json
from sklearn.metrics import classification_report
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import plot_confusion_matrix
import matplotlib.pyplot as plt
from tqdm import tqdm

from sklearn.linear_model import SGDClassifier
from time import time
from datetime import datetime
import spacy
### Фічі для моделі
def feachure_extractor(sent):
    feachure_sent = []
    #doc = nlp(' '.join(sent))
    doc = sent

    for i, word in enumerate(doc):
        features = dict()
        #features['word'] = word
        features["word-1"] = doc[i-1] if i > 0 else "NONE"
        features['is title'] = word.istitle()
        features['start'] = True if not i else False
        features['end'] = True if i == len(doc) - 1 else False
        #features['is_upper'] = word.isupper()
        #features["parent"] = sentence[i].dep_ + "_" + sentence[i].head.lemma_
        #features["right-bigram"] = sentence[i+1].text + "_" + sentence[i+2].text if i < (len(sentence) - 2) else "NONE"
        feachure_sent.append(features)
    return feachure_sent

def benchmark(X_train, X_val, X_test, y_train, y_val,y_test, pipeline, parameters, label=''):
    now = datetime.now()
    date_time = now.strftime("%m-%d-%Y__%H-%M-%S")
    with open('./iterations/' + pipeline[1].__class__.__name__ + '-' + label + '--' + date_time, 'w+') as f:
        grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=1)

        print("Performing grid search...")
        print("pipeline:", [name for name, _ in pipeline.steps])
        print("pipeline:", [name for name, _ in pipeline.steps], file=f)
        print("\n", file=f)
        print(parameters, file=f)
        print("\n", file=f)

        print("parameters:")
        print(parameters)
        t0 = time()
        grid_search.fit(X_train, y_train)
        print("done in %0.3fs" % (time() - t0))
        print()
        print("Best score: %0.3f" % grid_search.best_score_)
        print("Best score: %0.3f" % grid_search.best_score_, file=f)
        print("Best parameters set:")
        best_parameters = grid_search.best_estimator_.get_params()
        for param_name in sorted(parameters.keys()):
            print("\t%s: %r" % (param_name, best_parameters[param_name]))
            print("\t%s: %r" % (param_name, best_parameters[param_name]), file=f)

        print("\n", file=f)

        ### validation report
        print('### Validation report')
        predicted = grid_search.predict(X_val)
        clf_repport = classification_report(y_val, predicted)
        print(clf_repport)
        print(clf_repport, file=f)

        # test report
        print('### Test report')
        predicted_test = grid_search.predict(X_test)
        clf_repport = classification_report(y_test, predicted_test)
        print(clf_repport)
        print(clf_repport, file=f)

        ## Confusion matrix print
        titles_options = [("Confusion matrix, without normalization", None),
                          ("Normalized confusion matrix", 'true')]
        for title, normalize in titles_options:
            disp = plot_confusion_matrix(grid_search, X_test, y_test,
                                 cmap=plt.cm.Blues,
                                 normalize=normalize)
        disp.ax_.set_title(title)

        print(title, file=f)
        print(disp.confusion_matrix,file=f)

        plt.show()


nlp = spacy.load("en_core_web_sm")
### загрузка данних
DATASET_FILE = 'dataset.json'
with open(DATASET_FILE) as file:
    dataset = json.load(file)

### підготовка дев датасету
print("Load DEV dataset....")
feachures_dataset = []
labels_dataset = []
for sent, labels in tqdm(zip(dataset['dev']['tokens'], dataset['dev']['labels'])):
    feachures_dataset.extend(feachure_extractor(sent))
    labels_dataset.extend(labels)


### Векторизація дев сету
vec = DictVectorizer()
vec = vec.fit(feachures_dataset)
#print("Total number of features: {}\nFeature list: {}".format(len(vec.get_feature_names()), vec.get_feature_names()))

features_vectorized = vec.transform(feachures_dataset)

# спліт  на дев та валідаційний
X_train, X_val, y_train, y_val = train_test_split(features_vectorized, labels_dataset, test_size=0.33, random_state=42)

### Підготовка тестового датасету
print("Load TEST dataset....")
test_feachures_dataset = []
test_labels_dataset = []
for sent, labels in tqdm(zip(dataset['test']['tokens'], dataset['test']['labels'])):
    test_feachures_dataset.extend(feachure_extractor(sent))
    test_labels_dataset.extend(labels)

X_test = vec.transform(test_feachures_dataset)
y_test = test_labels_dataset

#lrc = LogisticRegression(random_state=42, solver="sag", multi_class="multinomial", max_iter=1000, verbose=1)

# lrc.fit(X_train, y_train)
#
# pred1 = lrc.predict(X_val)
# print(classification_report(y_val, pred1))

features_vectorized = vec.transform(feachures_dataset)

X_train, X_val, y_train, y_val = train_test_split(features_vectorized, labels_dataset, test_size=0.33, random_state=42)

parameters = {
    #'vect__max_df': (0.5, 0.75, 1.0),
    #'vect__max_features': (None, 500, 1000, 2000, 5000),
    #'vect__ngram_range': ((1, 1), (1, 2), (1, 3)),  # unigrams or bigrams or thrigrams
    'tfidf__use_idf': (True, False),
    'tfidf__norm': ('l1', 'l2'),
    'clf__tol': (0.0001,),
    'clf__solver': ('sag',),
    'clf__penalty': ('l2', ),
    'clf__max_iter': (1000,),
    'clf__random_state': (42,)

}
# Побачити параметри для любого елемента пайплайну
#print(pipeline['clf'].get_params().keys())

pipeline = Pipeline([
    #('vect', DictVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', LogisticRegression()),
])

benchmark(X_train, X_val,X_test, y_train, y_val, y_test, pipeline, parameters)