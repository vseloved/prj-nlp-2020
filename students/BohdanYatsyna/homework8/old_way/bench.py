from datetime import datetime
from time import time

import matplotlib.pyplot as plt
from sklearn.metrics import plot_confusion_matrix, classification_report
from sklearn.model_selection import GridSearchCV

def run(pipeline, parameters, X_train, y_train, X_test, y_test, label=''):
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
