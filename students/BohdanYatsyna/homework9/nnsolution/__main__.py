import numpy as np
import json
from keras.utils import to_categorical
import plac
import sys
from tqdm import tqdm
from kerras_entailment import build_model
from spacy_hook import get_embeddings, KerasSimilarityShim
import wandb

try:
    import cPickle as pickle
except ImportError:
    import pickle

import spacy

# workaround for keras/tensorflow bug
# see https://github.com/tensorflow/tensorflow/issues/3388
import os
import importlib
from keras import backend as K


# def set_keras_backend(backend):
#     if K.backend() != backend:
#         os.environ["KERAS_BACKEND"] = backend
#         importlib.reload(K)
#         assert K.backend() == backend
#     if backend == "tensorflow":
#         K.get_session().close()
#         cfg = K.tf.ConfigProto()
#         cfg.gpu_options.allow_growth = True
#         K.set_session(K.tf.Session(config=cfg))
#         K.clear_session()

def train(train_loc, dev_loc, shape, settings):
    train_texts1, train_texts2, train_labels = read_snli(train_loc)
    dev_texts1, dev_texts2, dev_labels = read_snli(dev_loc)

    print("Loading spaCy")
    #nlp = spacy.load("en_vectors_web_lg")
    nlp = spacy.load("en_core_web_md")
    assert nlp.path is not None
    print("Processing texts...")
    train_X = create_dataset(nlp, train_texts1, train_texts2, 100, shape[0], "train")
    dev_X = create_dataset(nlp, dev_texts1, dev_texts2, 100, shape[0], "dev")

    print("Compiling network")
    embed = get_embeddings(nlp.vocab)
    model = build_model(embed, shape, settings)

    print(settings)
    model.fit(
        train_X,
        train_labels,
        validation_data=(dev_X, dev_labels),
        epochs=settings["nr_epoch"],
        batch_size=settings["batch_size"],
    )
    if not (nlp.path / "similarity").exists():
        (nlp.path / "similarity").mkdir()
    print("Saving to", nlp.path / "similarity")
    weights = model.get_weights()
    # remove the embedding matrix.  We can reconstruct it.
    del weights[1]
    with (nlp.path / "similarity" / "model").open("wb") as file_:
        pickle.dump(weights, file_)
    with (nlp.path / "similarity" / "config.json").open("w") as file_:
        file_.write(model.to_json())


def evaluate(dev_loc, shape):
    dev_texts1, dev_texts2, dev_labels = read_snli(dev_loc)
    nlp = spacy.load("en_core_web_md")
    nlp.add_pipe(KerasSimilarityShim.load(nlp.path / "similarity", nlp, shape[0]))
    total = 0.0
    correct = 0.0
    for text1, text2, label in zip(dev_texts1, dev_texts2, dev_labels):
        doc1 = nlp(text1)
        doc2 = nlp(text2)
        sim, _ = doc1.similarity(doc2)
        if sim == KerasSimilarityShim.entailment_types[label.argmax()]:
            correct += 1
        total += 1
    return correct, total


def demo(shape):
    nlp = spacy.load("en_core_web_md")
    nlp.add_pipe(KerasSimilarityShim.load(nlp.path / "similarity", nlp, shape[0]))

    doc1 = nlp("The king of France is bald.")
    doc2 = nlp("France has no king.")

    print("Sentence 1:", doc1)
    print("Sentence 2:", doc2)

    entailment_type, confidence = doc1.similarity(doc2)
    print("Entailment type:", entailment_type, "(Confidence:", confidence, ")")


LABELS = {"entailment": 0, "contradiction": 1, "neutral": 2}


def read_snli(path):
    texts1 = []
    texts2 = []
    labels = []
    with open(path, "r") as file_:
        for line in file_:
            eg = json.loads(line)
            label = eg["gold_label"]
            if label == "-":  # per Parikh, ignore - SNLI entries
                continue
            texts1.append(eg["sentence1"])
            texts2.append(eg["sentence2"])
            labels.append(LABELS[label])
    return texts1, texts2, to_categorical(np.asarray(labels, dtype="int32"))


def create_dataset(nlp, texts, hypotheses, num_unk, max_length, dataset_label):
    sents = texts + hypotheses
    sents_as_ids = []
    n_jobs = 4
    batch_size = 1024
    processed_sents = list(nlp.pipe(tqdm(sents), n_process=n_jobs, batch_size=batch_size))
    for doc in tqdm(processed_sents, desc=f"Reading {dataset_label} dataset "):
        word_ids = []
        for i, token in enumerate(doc):
            # skip odd spaces from tokenizer
            if token.has_vector and token.vector_norm == 0:
                continue

            if i > max_length:
                break

            if token.has_vector:
                word_ids.append(token.rank + num_unk + 1)
            else:
                # if we don't have a vector, pick an OOV entry
                word_ids.append(token.rank % num_unk + 1)

        # there must be a simpler way of generating padded arrays from lists...
        word_id_vec = np.zeros((max_length), dtype="int")
        clipped_len = min(max_length, len(word_ids))
        word_id_vec[:clipped_len] = word_ids[:clipped_len]
        sents_as_ids.append(word_id_vec)

    return [np.array(sents_as_ids[: len(texts)]), np.array(sents_as_ids[len(texts) :])]


@plac.annotations(
    mode=("Mode to execute", "positional", None, str, ["train", "evaluate", "demo"]),
    train_loc=("Path to training data", "option", "t", str),
    dev_loc=("Path to development or test data", "option", "s", str),
    max_length=("Length to truncate sentences", "option", "L", int),
    nr_hidden=("Number of hidden units", "option", "H", int),
    dropout=("Dropout level", "option", "d", float),
    learn_rate=("Learning rate", "option", "r", float),
    batch_size=("Batch size for neural network training", "option", "b", int),
    nr_epoch=("Number of training epochs", "option", "e", int),
    entail_dir=(
            "Direction of entailment",
            "option",
            "D",
            str,
            ["both", "left", "right"],
    ),
)
def main(
        mode,
        train_loc="../snli_1.0/snli_1.0_train.jsonl",
        dev_loc="../snli_1.0/snli_1.0_dev.jsonl",
        max_length=50,
        nr_hidden=200,
        dropout=0.2,
        learn_rate=0.001,
        batch_size=1024,
        nr_epoch=20,
        entail_dir="both",
):
    shape = (max_length, nr_hidden, 3)
    settings = {
        "lr": learn_rate,
        "dropout": dropout,
        "batch_size": batch_size,
        "nr_epoch": nr_epoch,
        "entail_dir": entail_dir,
    }

    if mode == "train":
        wandb.init(magic=True)
        if train_loc == None or dev_loc == None:
            print("Train mode requires paths to training and development data sets.")
            sys.exit(1)
        train(train_loc, dev_loc, shape, settings)

    elif mode == "evaluate":
        if dev_loc == None:
            print("Evaluate mode requires paths to test data set.")
            sys.exit(1)
        correct, total = evaluate(dev_loc, shape)
        print(correct, "/", total, correct / total)
    else:
        demo(shape)


if __name__ == "__main__":
    plac.call(main)