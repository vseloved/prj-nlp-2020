from collections import OrderedDict
from collections import defaultdict
from enum import Enum

ROOT = OrderedDict([('id', 0), ('form', 'ROOT'), ('lemma', 'ROOT'), ('upostag', 'ROOT'),
                    ('xpostag', None), ('feats', None), ('head', None), ('deprel', None),
                    ('deps', None), ('misc', None)])


class Actions(str, Enum):
    SHIFT = "shift"
    RIGHT = "right"
    LEFT = "left"
    REDUCE = "reduce"


class Configuration:
    arcs, buffer, stack, deps, features, labels = [], [], [], [], [], []
    sentence = None

    def __init__(self, buf, s):
        self.buffer = buf
        self.sentence = s
        self.stack, deps = [ROOT], []

    def __init__(self, tree, oracle, feature_extractor):
        self.features, self.labels = [], []
        self.stack, self.buffer, deps = [ROOT], tree[:], []
        while self.buffer or self.stack:
            action = oracle.predict(self)
            self.features.append(feature_extractor(self))
            self.labels.append(action.value)
            if action == Actions.SHIFT:
                self.stack.append(self.buffer.pop(0))
            elif action == Actions.REDUCE:
                self.stack.pop()
            elif action == Actions.LEFT:
                self.deps.append((self.stack[-1]["id"], self.buffer[0]["id"]))
                self.stack.pop()
            elif action == Actions.RIGHT:
                self.deps.append((self.buffer[0]["id"], self.stack[-1]["id"]))
                self.stack.append(self.buffer.pop(0))
            else:
                print("Unknown action.")


class GoldConfiguration:
    def __init__(self):
        self.heads = {}
        self.deps = defaultdict(lambda: [])


class Classifier:
    def __init__(self, weights, labels):
        self.weights = weights
        self.labels = labels

    def score(self, fv):

        scores = dict((label, 0) for label in self.labels)

        for k, v in fv.items():

            if v == 0:
                continue
            if k not in self.weights:
                continue

            wv = self.weights[k]

            for label, weight in wv.items():
                scores[label] += weight * v

        return scores


class Oracle:
    predict = None

    def __init__(self):
        self.predict = self.stat_predict

    def stat_predict(self, conf: Configuration):
        """
        Make a decision on the right action to do.
        """
        top_stack = conf.stack[-1] if len(conf.stack) else None
        top_queue = conf.buffer[0] if len(conf.buffer) else None

        # check if both stack and queue are non-empty
        if top_stack and not top_queue:
            return Actions.REDUCE
        # check if there are any clear dependencies
        elif top_queue["head"] == top_stack["id"]:
            return Actions.RIGHT
        elif top_stack["head"] == top_queue["id"]:
            return Actions.LEFT
        # check if we can reduce the top of the stack
        elif top_stack["id"] in [i[0] for i in conf.deps] and \
                (top_queue["head"] < top_stack["id"] or \
                 [s for s in conf.stack if s["head"] == top_queue["id"]]):
            return Actions.REDUCE
        # default option
        else:
            return Actions.SHIFT


def is_non_projective(tree):
    relations = [[i['id'], i['head']] for i in tree if type(i["id"]) == int]
    for rel in relations:
        for ref_rel in relations:
            a, c = sorted(rel)
            b, d = sorted(ref_rel)
            if a < b and b < c and c < d:
                return True
    return False


def filter_non_projective(trees):
    gold_proj = []
    for tre in trees:
        if not is_non_projective(tre):
            gold_proj.append(tre)
    return gold_proj
