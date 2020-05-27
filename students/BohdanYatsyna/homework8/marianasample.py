from collections import OrderedDict
from conllu import parse
from enum import Enum
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


class Actions(str, Enum):
    SHIFT = "shift"
    REDUCE = "reduce"
    RIGHT = "right"
    LEFT = "left"

def oracle(stack, top_queue, relations):
    """
    Make a decision on the right action to do.
    """
    top_stack = stack[-1]
    # check if both stack and queue are non-empty
    if top_stack and not top_queue:
        return Actions.REDUCE
    # check if there are any clear dependencies
    elif top_queue["head"] == top_stack["id"]:
        return Actions.RIGHT
    elif top_stack["head"] == top_queue["id"]:
        return Actions.LEFT
    # check if we can reduce the top of the stack
    elif top_stack["id"] in [i[0] for i in relations] and \
            (top_queue["head"] < top_stack["id"] or \
             [s for s in stack if s["head"] == top_queue["id"]]):
        return Actions.REDUCE
    # default option
    else:
        return Actions.SHIFT

def get_data(tree):
    features, labels = [], []
    stack, queue, relations = [ROOT], tree[:], []

    while queue or stack:
        action = oracle(stack if len(stack) > 0 else None,
                        queue[0] if len(queue) > 0 else None,
                        relations)
        features.append(extract_features(stack, queue))
        labels.append(action.value)
        if action == Actions.SHIFT:
            stack.append(queue.pop(0))
        elif action == Actions.REDUCE:
            stack.pop()
        elif action == Actions.LEFT:
            relations.append((stack[-1]["id"], queue[0]["id"]))
            stack.pop()
        elif action == Actions.RIGHT:
            relations.append((queue[0]["id"], stack[-1]["id"]))
            stack.append(queue.pop(0))
        else:
            print("Unknown action.")
    return features, labels

def dep_parse(sentence, oracle, vectorizer, log=True):
    stack, queue, relations = [ROOT], sentence[:], []
    while queue or stack:
        if stack and not queue:
            stack.pop()
        else:
            features = extract_features(stack, queue)
            action = oracle.predict(vectorizer.transform([features]))[0]
            # actual parsing
            if action == Actions.SHIFT:
                stack.append(queue.pop(0))
            elif action == Actions.REDUCE:
                stack.pop()
            elif action == Actions.LEFT:
                relations.append((stack[-1]["id"], queue[0]["id"]))
                stack.pop()
            elif action == Actions.RIGHT:
                relations.append((queue[0]["id"], stack[-1]["id"]))
                stack.append(queue.pop(0))
            else:
                print("Unknown action.")
    return sorted(relations)

def extract_features(stack, queue):
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










PATH = "."

with open(PATH + "/uk_iu-ud-train.conllu", "r") as f:
    train_trees = parse(f.read())

with open(PATH + "/uk_iu-ud-dev.conllu", "r") as f:
    test_trees = parse(f.read())

ROOT = OrderedDict([('id', 0), ('form', 'ROOT'), ('lemma', 'ROOT'), ('upostag', 'ROOT'),
                    ('xpostag', None), ('feats', None), ('head', None), ('deprel', None),
                    ('deps', None), ('misc', None)])

train_features, train_labels = [], []
for tree in train_trees:
    tree_features, tree_labels = get_data([t for t in tree if type(t["id"])==int])
    train_features += tree_features
    train_labels += tree_labels

print(len(train_features), len(train_labels))

test_features, test_labels = [], []
for tree in test_trees:
    tree_features, tree_labels = get_data([t for t in tree if type(t["id"])==int])
    test_features += tree_features
    test_labels += tree_labels

print(len(test_features), len(test_labels))

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

total, tp, full_match = 0, 0, 0
for tree in test_trees:
    tree = [t for t in tree if type(t["id"])==int]
    golden = [(node["id"], node["head"]) for node in tree]
    predicted = dep_parse(tree, lrc, vec, log=False)
    total += len(tree)
    tp += len(set(golden).intersection(set(predicted)))
    if set(golden) == set(predicted):
        full_match += 1

print("Total:", total)
print("Correctly defined:", tp)
print("UAS:", round(tp/total, 2))
print("Full match:", round(full_match/len(test_trees), 2))
