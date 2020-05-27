import argparse
import students.BohdanYatsyna.homework8.fileio as fileio
import students.BohdanYatsyna.homework8.arc as arc
import students.BohdanYatsyna.homework8.features as features
from tqdm import tqdm
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import pickle

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Sample program showing training and testing dependency parsers")
    parser.add_argument('--parser', help='Parser type (eager|hybrid) (default: eager)', default='eager')
    parser.add_argument('--train', help='CONLL training file', default='uk_iu-ud-train.conllu')
    parser.add_argument('--test', help='CONLL testing file', default='uk_iu-ud-test.conllu')
    parser.add_argument('--fx', help='Feature extractor', default='ex')
    parser.add_argument('--n', help='Number of passes over training data', default=15, type=int)
    parser.add_argument('-v', action='store_true')
    opts = parser.parse_args()

    actions_list = [a for a in arc.Actions]

    train_trees = fileio.read_conll_deps(opts.train)
    test_trees = fileio.read_conll_deps(opts.test)

    train_gold = arc.filter_non_projective(train_trees)
    test_gold = arc.filter_non_projective(test_trees)
    #model = arc.Classifier({},actions_list)

    # define oracle and feature extractor
    oracle = arc.Oracle()
    feature_extractor = features.extract
    # Load test and train data

    train_features, train_labels = features.get_features_labels("train",train_trees,oracle,feature_extractor)
    test_features, test_labels = features.get_features_labels("test",test_trees,oracle,feature_extractor)

    vectorizer = DictVectorizer()
    vec = vectorizer.fit(train_features)
    print("\nTotal number of features: ", len(vec.get_feature_names()))

    train_features_vectorized = vec.transform(train_features)
    test_features_vectorized = vec.transform(test_features)

    print(len(train_features_vectorized.toarray()), len(test_features_vectorized.toarray()))

    lrc = LogisticRegression(random_state=42, solver="saga", multi_class="multinomial", max_iter=600, verbose=1, n_jobs=-1)
    lrc.fit(train_features_vectorized, train_labels)

    predicted = lrc.predict(test_features_vectorized)
    print(classification_report(test_labels, predicted))

    # total, tp, full_match = 0, 0, 0
    # for tree in test_trees:
    #     tree = [t for t in tree if type(t["id"])==int]
    #     golden = [(node["id"], node["head"]) for node in tree]
    #     predicted = dep_parse(tree, lrc, vec, log=False)
    #     total += len(tree)
    #     tp += len(set(golden).intersection(set(predicted)))
    #     if set(golden) == set(predicted):
    #         full_match += 1

    # print("Total:", total)
    # print("Correctly defined:", tp)
    # print("UAS:", round(tp/total, 2))
    # print("Full match:", round(full_match/len(test_trees), 2))