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
import numpy as np

from time import time
from datetime import datetime

'''Best score: 0.986
clf__max_iter: 1000
clf__penalty: 'l2'
clf__random_state: 42
clf__solver: 'sag'
clf__tol: 0.0001
tfidf__norm: 'l1'
tfidf__use_idf: True'''

clf = LogisticRegression(max_iter=1000, penalty='l2',random_state=42,solver='sag',tol=0.0001,multi_class='multinomial')
pipeline = Pipeline([
    ('tfidf', TfidfTransformer(norm='l1',use_idf=False)),
    ('clf', clf),
])

print("Load dataset....")
### загрузка данних
DATASET_FILE = 'dataset.json'
with open(DATASET_FILE) as file:
    dataset = json.load(file)

print("Fit  DictVector....")
### Векторизація дев сету
vec = DictVectorizer()
vec = vec.fit(dataset['dev']['tokens'])
# print("Total number of features: {}\nFeature list: {}".format(len(vec.get_feature_names()), vec.get_feature_names()))

features_vectorized = vec.transform(dataset['dev']['tokens'])
labels_dataset = dataset['dev']['labels']
# спліт  на дев та валідаційний
X_train, X_val, y_train, y_val = train_test_split(features_vectorized, labels_dataset, test_size=0.33, random_state=42)

X_test = vec.transform(dataset['test']['tokens'])
y_test = dataset['test']['labels']

print("Train  pipeline....")
pipeline.fit(X_train,y_train)

### validation report
print('### Validation report')
predicted = pipeline.predict(X_test)
clf_repport = classification_report(y_test, predicted)
print(clf_repport)
#print(clf_repport, file=f)

## Confusion matrix print
titles_options = [("Confusion matrix, without normalization", None),
                  ("Normalized confusion matrix", 'true')]
for title, normalize in titles_options:
    disp = plot_confusion_matrix(pipeline, X_test, y_test,
                                 cmap=plt.cm.Blues,
                                 normalize=normalize)
disp.ax_.set_title(title)

plt.show()

"""Prints features with the highest coefficient values, per class"""
feature_names = vec.get_feature_names()
for i, class_label in enumerate(clf.classes_):
    top10 = np.argsort(clf.coef_[i])[-10:]
    print("%s: %s" % (class_label,
                      " ".join(feature_names[j] for j in top10)))