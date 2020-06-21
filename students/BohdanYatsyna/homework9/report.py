import wandb
from sklearn.metrics import classification_report, accuracy_score

def wandb_classification_report(clf, X_dev, X_test, y_dev, y_test, wandb):

    dev_y_pred = clf.predict(X_dev)
    test_y_pred = clf.predict(X_test)

    print(classification_report(y_dev, dev_y_pred))
    dev_clf_report = classification_report(y_dev, dev_y_pred, output_dict=True)

    print(classification_report(y_test, test_y_pred))
    test_clf_report = classification_report(y_test, test_y_pred, output_dict=True)

    data_dev = []
    for r in dev_clf_report:
        if type(dev_clf_report[r]) == float:
            data_dev += [[r, '', '', round(dev_clf_report[r],4), '']]
        else:
            data_dev += [[r, str(round(dev_clf_report[r]['precision'], 4)), str(round(dev_clf_report[r]['recall'], 4)),
                      str(round(dev_clf_report[r]['f1-score'], 4)), str(round(dev_clf_report[r]['support'], 4))]]

    data_test = []
    for r in test_clf_report:
        if type(test_clf_report[r]) == float:
            data_test += [[r, '', '', round(test_clf_report[r],4), '']]
        else:
            data_test += [[r, str(round(test_clf_report[r]['precision'], 4)), str(round(test_clf_report[r]['recall'], 4)),
                      str(round(test_clf_report[r]['f1-score'], 4)), str(round(test_clf_report[r]['support'], 4))]]


    wandb.log({"examples": wandb.Table(data=data_dev, columns=["name", "precision", "recall", "f1-score", "support"])})
    wandb.log({"dev accuracy_score": accuracy_score(y_dev, dev_y_pred)})

    wandb.log({"examples": wandb.Table(data=data_test, columns=["name", "precision", "recall", "f1-score", "support"])})
    wandb.log({"test accuracy_score": accuracy_score(y_test, test_y_pred)})

    # visualize model
    #wandb.sklearn.plot_classifier(clf, X_train, X_test, y_train, y_test, dev_y_pred, y_probas, clf.classes_, True, name, feature_names=None)
    wandb.sklearn.plot_confusion_matrix(y_dev, dev_y_pred, clf.classes_)
    wandb.sklearn.plot_confusion_matrix(y_test, test_y_pred, clf.classes_)
