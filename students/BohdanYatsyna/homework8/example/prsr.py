import random
import numpy as np
import itertools
from nltk import ParserI
from students.BohdanYatsyna.homework8.example.cls import DependencyParse, ParserState, Transitions
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import SGDClassifier

class Parser(ParserI):

    @staticmethod
    def build_transition_dataset(parses, feature_extractor):
        """ Transform a list of parses to a dataset """
        transitions_X, transitions_y = [], []
        for gold_parse in parses:
            # Init an empty parse
            dep_parse = DependencyParse(gold_parse.tagged_words()[1:-1])

            # Start from an empty state
            state = ParserState(dep_parse)

            while state.stack or (state.buffer_index + 1) < len(dep_parse):
                features = feature_extractor(state)
                gold_moves = state.next_gold(gold_parse)

                if not gold_moves:
                    # Something is wrong here ...
                    break

                # Pick one of the possible transitions
                t = random.choice(gold_moves)

                # Append the features and transition to the dataset
                transitions_X.append(features)
                transitions_y.append(t)

                # Apply the transition to the state
                state.apply(t)

        return transitions_X, transitions_y

    def __init__(self, feature_detector):
        self.feature_extractor = feature_detector
        self._vectorizer = FeatureHasher()
        self._model = SGDClassifier(loss='modified_huber')

    def evaluate(self, parses):
        correct, total = 0, 0

        for parse in parses:
            predicted_parse = self.parse(parse.tagged_words()[1:-1])
            heads, predicted_heads = np.array(parse.heads()[1:]), np.array(predicted_parse.heads()[1:])
            total += len(heads)
            correct += np.sum(heads == predicted_heads)
        return correct / total

    def parse(self, sent, *args, **kwargs):
        """ Parse a tagged sentence """
        state = ParserState(DependencyParse(sent))

        while state.stack or (state.buffer_index + 1) < len(state.parse):
            # Extract the features of the current state
            features = self.feature_extractor(state)
            vectorized_features = self._vectorizer.transform([features])

            # Get probabilities for the next transitions
            predictions = self._model.predict_proba(vectorized_features)[0]
            scores = dict(zip(list(self._model.classes_), list(predictions)))

            # Check what moves are actually valid
            valid_moves = state.next_valid()

            # Get the most probable valid mode
            guess = max(valid_moves, key=lambda move: scores[move])

            # apply the transition to the state
            state.apply(guess)

        return state.parse

    def train(self, corpus_iterator, n_iter=5, batch_size=100):
        """ Train a model on a given corpus """
        for _ in range(n_iter):
            # Fork the iterator
            corpus_iterator, parses = itertools.tee(corpus_iterator)
            batch_count = 0
            while True:
                batch_count += 1
                print("Training on batch={0}".format(batch_count))
                batch = list(itertools.islice(parses, batch_size))

                # No more batches
                if not batch:
                    break

                # Train the model on a batch
                self.train_batch(batch)

    def train_batch(self, gold_parses):
        """ Train the model on a single batch """
        t_X, t_Y = self.build_transition_dataset(
            gold_parses, self.feature_extractor)

        self._model.partial_fit(self._vectorizer.transform(t_X), t_Y,
                                classes=Transitions.ALL)