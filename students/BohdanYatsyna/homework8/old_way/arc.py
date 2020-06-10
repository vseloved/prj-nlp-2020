from collections import OrderedDict, defaultdict
from enum import Enum

ROOT = OrderedDict([('id', 0), ('form', 'ROOT'), ('lemma', 'ROOT'), ('upostag', 'ROOT'),
                    ('xpostag', None), ('feats', None), ('head', None), ('deprel', None),
                    ('deps', None), ('misc', None)])


class Actions(str, Enum):
    SHIFT = "shift"
    RIGHT = "right"
    LEFT = "left"
    REDUCE = "reduce"

class GoldConfiguration:
    def __init__(self):
        self.heads = {}
        self.deps = defaultdict(lambda: [])

class Configuration:

    def __init__(self, tree, oracle, feature_extractor, vectorizer=None, parse=True):
        self.features, self.labels = [], []
        self.stack, self.buffer, self.deps = [ROOT], tree[:], []
        self.tree = tree
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

    def get_gold_conf(self):
        gold_conf = GoldConfiguration()
        gold_conf.heads[0] = None
        for dep in self.tree:
            head = dep['head']
            gold_conf.heads[dep['id']] = dep['head']
            if head not in gold_conf.deps:
                gold_conf.deps[head] = []
            gold_conf.deps[head].append(dep['id'])
        return gold_conf

    def legal(self):
        transitions = []
        left_ok = right_ok = shift_ok = True
        reduce_ok = False
        if len(self.stack) < 2:
            right_ok = False
        if len(self.stack) == 0 or self.stack[-1] == ROOT:
            left_ok = False

        top_stack = self.stack[-1] if len(self.stack) else None
        top_queue = self.buffer[0] if len(self.buffer) else None

        if top_stack and not top_queue or \
                top_stack["id"] in [i[0] for i in self.deps] and \
                (top_queue["head"] < top_stack["id"] or \
                 [s for s in self.stack if s["head"] == top_queue["id"]]):
            reduce_ok = True


        if shift_ok is True:
            transitions.append(Actions.SHIFT)
        if right_ok is True:
            transitions.append(Actions.RIGHT)
        if left_ok is True:
            transitions.append(Actions.LEFT)
        if reduce_ok is True:
            transitions.append(Actions.REDUCE)
        return transitions

    def zero_cost_right(self, gold_conf):
        """
        Adding the arc (s1, s0) and popping s0 from the stack means that s0 will not be able
        to acquire heads or deps from B.  The cost is the number of arcs in gold_conf of the form
        (s0, d) and (h, s0) where h, d in B.  For non-zero cost moves, we are looking simply for
        (s0, b) or (b, s0) for all b in B
        :param conf:
        :param gold_conf:
        :return:
        """

        s0 = self.stack[-1] if len(self.stack) else None
        for b in self.buffer:
            if (b['id'] in gold_conf.heads and gold_conf.heads[b['id']] is s0['id']) or gold_conf.heads[s0['id']] is b['id']:
                return False
        return True

    def zero_cost_left(self, gold_conf):
        """
        Adding the arc (b, s0) and popping s0 from the stack means that s0 will not be able to acquire
        heads from H = {s1} U B and will not be able to acquire dependents from B U b, therefore the cost is
        the number of arcs in T of form (s0, d) or (h, s0), h in H, d in D

        To have cost, then, only one instance must occur

        :param conf:
        :param gold_conf:
        :return:
        """

        s0 = self.stack[-1] if len(self.stack) else None
        s1 = len(self.stack) > 2 and self.stack[-2] or None

        for dep in gold_conf.deps[s0['id']]:
            for b in self.buffer:
                if dep == b['id']: return False


        H = self.buffer[1:] + [s1['id']]
        if gold_conf.heads[s0['id']] in H:
            return False
        return True

    def zero_cost_shift(self, gold_conf):
        """
        Pushing b onto the stack means that b will not be able to acquire
        heads from H = {s1} U S and will not be able to acquire deps from
        D = {s0, s1} U S
        :param conf:
        :param gold_conf:
        :return:
        """
        if len(self.buffer) < 1:
            return False
        if len(self.stack) == 0:
            return True

        b = self.buffer[0]
        # Cost is the number of arcs in T of the form (s0, d) and (h, s0) for h in H and d in D
        if b['id'] in gold_conf.heads and gold_conf.heads[b['id']] in self.stack[0:-1]:
            return False
        for dep in self.stack:
            if dep['id'] in gold_conf.deps[b['id']] : return False
        #ll = len(list(filter(lambda dep: dep in self.stack, gold_conf.deps[b['id']])))
        return True

class Oracle:
    def __init__(self, dynamic=False):
        if dynamic:
            self.predict = self.dyn_predict
        else:
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

    def dyn_predict(self, conf: Configuration):
        """
        Make a decision on the right action to do.
        """
        zero_cost_right_ok = zero_cost_left_ok = zero_cost_shift_ok = False
        legal_transitions = conf.legal()

        print(legal_transitions)

        gold_conf = conf.get_gold_conf()

        zero_cost_right_ok = conf.zero_cost_right(gold_conf)
        zero_cost_left_ok = conf.zero_cost_left(gold_conf)
        zero_cost_shift_ok = conf.zero_cost_shift(gold_conf)
        print('==============')
        print("Zero cost right - {}".format(zero_cost_right_ok))
        print("Zero cost left - {}".format(zero_cost_left_ok))
        print("Zero cost shift - {}".format(zero_cost_shift_ok))
        print('==============')

        ###TODO remove old stat_predict code
        options = []
        if Actions.SHIFT in legal_transitions and conf.zero_cost_shift(gold_conf):
            options.append(Actions.SHIFT)
        if Actions.RIGHT in legal_transitions and conf.zero_cost_right(gold_conf):
            options.append(Actions.RIGHT)
        if Actions.LEFT in legal_transitions and conf.zero_cost_left(gold_conf):
            options.append(Actions.LEFT)
        if Actions.REDUCE in legal_transitions:
            options.append(Actions.REDUCE)

        print(options)
        t = 1



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
