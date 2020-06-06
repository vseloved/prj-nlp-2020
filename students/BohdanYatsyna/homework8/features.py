# from students.BohdanYatsyna.homework8.arc import Configuration
import pickle

from tqdm import tqdm

from students.BohdanYatsyna.homework8 import arc


def extract(conf: arc.Configuration):
    stack = conf.stack
    queue = conf.buffer
    features = dict()

    if len(stack) > 0:
        stack_top = stack[-1]
        features["s0-word"] = stack_top["form"]
        features["s0-lemma"] = stack_top["lemma"]
        features["s0-tag"] = stack_top["upostag"]
    if len(stack) > 1:
        features["s1-tag"] = stack[-2]["upostag"]
    if queue:
        queue_top = queue[0]
        features["q0-word"] = queue_top["form"]
        features["q0-lemma"] = queue_top["lemma"]
        features["q0-tag"] = queue_top["upostag"]
    if len(queue) > 1:
        queue_next = queue[1]
        features["q1-word"] = queue_next["form"]
        features["q1-tag"] = queue_next["upostag"]
    if len(queue) > 2:
        features["q2-tag"] = queue[2]["upostag"]
    if len(queue) > 3:
        features["q3-tag"] = queue[3]["upostag"]
    return features


def get_features_labels(name, trees, oracle, feature_extractor):
    features, labels = [],[]
    try:
        with open(name + '_features.pickle', 'rb') as f:
            features = pickle.load(f)
        with open(name + '_labels.pickle', 'rb') as f:
            labels = pickle.load(f)

        conf = arc.Configuration([t for t in trees[0] if type(t["id"]) == int], oracle, feature_extractor)
        if features[1] != conf.features[1]: raise Exception("Datasaved in file different")
        if labels[1] != conf.labels[1]: raise Exception("Datasaved in file different")

        print("Loading " + name + " dataset  - compleate")
    except:
        features, labels = [],[]
        for tree in tqdm(trees, desc="Loading " + name + " dataset"):
            tokens = [t for t in tree if type(t["id"]) == int]
            conf = arc.Configuration(tokens, oracle, feature_extractor)
            features += conf.features
            labels += conf.labels

        # dump calculated data to file
        with open(name + '_features.pickle', 'wb') as f:
            pickle.dump(features, f)

        with open(name + '_labels.pickle', 'wb') as f:
            pickle.dump(labels, f)
    finally:
        return features, labels