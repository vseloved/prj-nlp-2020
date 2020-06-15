import wandb
from sklearn.metrics import classification_report, accuracy_score

def wandb_classification_report(clf, X_train, X_test, y_train, y_test, name, wandb):
    y_pred = clf.predict(X_test)
    #y_probas = clf.predict_proba(X_test)

    print(classification_report(y_test, y_pred))
    clf_report = classification_report(y_test, y_pred, output_dict=True)

    data = []
    for r in clf_report:
        if type(clf_report[r]) == float:
            data += [[r, '', '', round(clf_report[r],4), '']]
        else:
            data += [[r, str(round(clf_report[r]['precision'], 4)), str(round(clf_report[r]['recall'], 4)),
                      str(round(clf_report[r]['f1-score'], 4)), str(round(clf_report[r]['support'], 4))]]

    wandb.log({"examples": wandb.Table(data=data, columns=["name", "precision", "recall", "f1-score", "support"])})
    wandb.log({"accuracy_score": accuracy_score(y_test, y_pred)})

    # visualize model
    #wandb.sklearn.plot_classifier(clf, X_train, X_test, y_train, y_test, y_pred, y_probas, clf.classes_, True, name, feature_names=None)
    wandb.sklearn.plot_confusion_matrix(y_test, y_pred, clf.classes_)