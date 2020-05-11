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


def benchmark(X_train, X_val, X_test, y_train, y_val, y_test, pipeline, parameters, label=''):
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
        print(disp.confusion_matrix, file=f)
        plt.show()

        """Prints features with the highest coefficient values, per class"""
        feature_names = vec.get_feature_names()
        for i, class_label in enumerate(grid_search.classes_):
            top10 = np.argsort(grid_search.coef_[i])[-10:]
            print("%s: %s" % (class_label,
                              " ".join(feature_names[j] for j in top10)))

print("Load dataset....")
### загрузка данних
DATASET_FILE = 'dataset.json'
with open(DATASET_FILE) as file:
    dataset = json.load(file)

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

X_train, X_val, y_train, y_val = train_test_split(features_vectorized, labels_dataset, test_size=0.33, random_state=42)

parameters = {
    'tfidf__use_idf': (True, False),
    'tfidf__norm': ('l1', 'l2'),
    'clf__tol': (0.0001,0.00001),
    'clf__solver': ('sag',),
    'clf__penalty': ('l2',),
    'clf__max_iter': (200,500, 1000,),
    'clf__random_state': (42,)

}
# Побачити параметри для любого елемента пайплайну
# print(pipeline['clf'].get_params().keys())

pipeline = Pipeline([
    ('tfidf', TfidfTransformer()),
    ('clf', LogisticRegression()),
])

grid_search = benchmark(X_train, X_val, X_test, y_train, y_val, y_test, pipeline, parameters)


#print_top10(vec,pipeline['clf'],pipeline['clf'].classes_)