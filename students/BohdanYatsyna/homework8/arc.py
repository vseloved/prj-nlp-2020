from collections import OrderedDict
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

    def __init__(self, tree, oracle, feature_extractor, vectorizer=None, parse=True):
        self.features, self.labels = [], []
        self.stack, self.buffer, self.deps = [ROOT], tree[:], []
        self.oracle = oracle
        self.feature_extractor = feature_extractor
        if parse: self.parse(vectorizer)

    def shift(self):
        self.stack.append(self.buffer.pop(0))

    def reduce(self):
        self.stack.pop()

    def arc_right(self):
        self.deps.append((self.buffer[0]["id"], self.stack[-1]["id"]))
        self.stack.append(self.buffer.pop(0))

    def arc_left(self):
        self.deps.append((self.stack[-1]["id"], self.buffer[0]["id"]))
        self.stack.pop()

    def parse(self, vectorizer=None):
        while self.buffer or self.stack:

            if vectorizer == None:
                action = self.oracle.predict(self)
            else:
                action = Actions(self.oracle.predict(vectorizer.transform(self.feature_extractor(self)))[0])

            self.features.append(self.feature_extractor(self))
            self.labels.append(action.value)

            if action == Actions.SHIFT:
                self.shift()
            elif action == Actions.REDUCE:
                self.reduce()
            elif action == Actions.LEFT:
                self.arc_left()
            elif action == Actions.RIGHT:
                self.arc_right()
            else:
                print("Unknown action.")


class Oracle:
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
