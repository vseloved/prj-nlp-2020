import argparse

import wandb
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from tqdm import tqdm

import students.BohdanYatsyna.homework8.old_way.arc as arc
import students.BohdanYatsyna.homework8.old_way.features as features
import students.BohdanYatsyna.homework8.old_way.fileio as fileio

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Sample program showing training and testing dependency parsers")
    parser.add_argument('--parser', help='Parser type (eager|hybrid) (default: eager)', default='eager')
    parser.add_argument('--train', help='CONLL training file', default='uk_iu-ud-train.conllu')
    parser.add_argument('--test', help='CONLL testing file', default='uk_iu-ud-test.conllu')
    parser.add_argument('--fx', help='Feature extractor', default='ex')
    parser.add_argument('--n', help='Number of passes over training data', default=15, type=int)
    parser.add_argument('-v', action='store_true')
    opts = parser.parse_args()

    wandb.init(project="homework8")

    actions_list = [a for a in arc.Actions]

    train_trees = fileio.read_conll_deps(opts.train)
    test_trees = fileio.read_conll_deps(opts.test)

    train_gold = arc.filter_non_projective(train_trees)
    test_gold = arc.filter_non_projective(test_trees)

    # define oracle and feature extractor
    oracle = arc.Oracle()
    feature_extractor = features.extract
    # Load test and train data

    train_features, train_labels = features.get_features_labels("train", train_trees, oracle, feature_extractor)
    test_features, test_labels = features.get_features_labels("test", test_trees, oracle, feature_extractor)

    vectorizer = DictVectorizer()
    vec = vectorizer.fit(train_features)
    print("\nTotal number of features: ", len(vec.get_feature_names()))

    train_features_vectorized = vec.transform(train_features)
    test_features_vectorized = vec.transform(test_features)

    print(len(train_features_vectorized.toarray()), len(test_features_vectorized.toarray()))

    model = LogisticRegression(random_state=42,tol=0.00001, solver="saga", multi_class="multinomial", max_iter=600, verbose=1,
                               n_jobs=-1)
    model.fit(train_features_vectorized, train_labels)

    predicted_labels = model.predict(test_features_vectorized)
    predicted_probas = model.predict_proba(test_features_vectorized)
    print(classification_report(test_labels, predicted_labels))
    clf_report = classification_report(test_labels, predicted_labels, output_dict=True)

    total, tp, full_match = 0, 0, 0
    for tree in tqdm(test_trees, desc="Evaluating test trees"):
        tree = [t for t in tree if type(t["id"]) == int]
        golden = [(node["id"], node["head"]) for node in tree]
        predicted = arc.Configuration(tree, model, feature_extractor, vec)
        total += len(tree)
        tp += len(set(golden).intersection(set(predicted.deps)))
        if set(golden) == set(predicted.deps):
            full_match += 1

    print("Total:", total)
    print("Correctly defined:", tp)
    print("UAS:", round(tp / total, 2))
    print("Full match:", round(full_match / len(test_trees), 2))

    data = []
    for r in clf_report:
        if type(clf_report[r]) == float:
            data += [[r, '', '', round(clf_report[r],4), '']]
        else:
            data += [[r, str(round(clf_report[r]['precision'], 4)), str(round(clf_report[r]['recall'], 4)),
                     str(round(clf_report[r]['f1-score'], 4)), str(round(clf_report[r]['support'], 4))]]

    wandb.log({"examples": wandb.Table(data=data, columns=["name", "precision", "recall", "f1-score", "support"])})
    wandb.log({"Total:": total,
               "Correctly defined": tp,
               "UAS": round(tp / total, 3),
               "Full match": round(full_match / len(test_trees), 3),
               "accuracy_score": accuracy_score(test_labels, predicted_labels)})

    # visualize model
    wandb.sklearn.plot_confusion_matrix(test_labels, predicted_labels, model.classes_)
    wandb.log({'pr': wandb.plots.precision_recall(test_labels, predicted_probas, actions_list)})
