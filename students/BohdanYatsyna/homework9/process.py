import operator
import os
import pickle
from functools import partial

import spacy
from joblib import Parallel, delayed
from spacy.util import minibatch
from tqdm import tqdm


def get_sentences(nlp, data, batch_size, n_jobs, label, name):
    data_dir = './data/'
    processed_sent1, processed_sent2, labels = [], [], []

    try:

        f_processed_sent1, f_processed_sent2, f_labels = [], [], []

        print("Loading " + name + " sent1 from file")
        with open(data_dir + name + '_sent1.pickle', 'rb') as f:
            f_processed_sent1 = pickle.load(f)
        print("Loading " + name + " sent2 from file")
        with open(data_dir + name + '_sent2.pickle', 'rb') as f:
            f_processed_sent2 = pickle.load(f)
        print("Loading " + name + " labels from file")
        with open(data_dir + name + '_labels.pickle', 'rb') as f:
            f_labels = pickle.load(f)
    except:
        print("Data can't be loaded")
        sent_list1 = map(operator.itemgetter('sentence1'), tqdm(data, desc=f'{label} Getting list of sentence1'))
        processed_sent1 = list(nlp.pipe(sent_list1, n_process=n_jobs, batch_size=batch_size))

        sent_list2 = map(operator.itemgetter('sentence2'), tqdm(data, desc=f'{label} Getting list of sentence2'))
        processed_sent2 = list(nlp.pipe(sent_list2, n_process=n_jobs, batch_size=batch_size))

        labels = list(map(operator.itemgetter('gold_label'), tqdm(data, desc=f'{label} Getting list of gold labels')))

        f_processed_sent1, f_processed_sent2, f_labels = [], [], []
        for i, l in enumerate(tqdm(labels, desc='Removing \'-\' class')):
            if l not in ['contradiction', 'entailment', 'neutral']:
                continue
            f_processed_sent1.append(processed_sent1[i])
            f_processed_sent2.append(processed_sent2[i])
            f_labels.append(labels[i])

        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
            print("Directory ", data_dir, " Created ")

        # dump calculated data to file
        with open(data_dir + name + '_sent1.pickle', 'wb') as f:
            pickle.dump(f_processed_sent1, f, protocol=-1)

        with open(data_dir + name + '_sent2.pickle', 'wb') as f:
            pickle.dump(f_processed_sent2, f, protocol=-1)

        with open(data_dir + name + '_labels.pickle', 'wb') as f:
            pickle.dump(f_labels, f, protocol=-1)

    finally:
        return f_processed_sent1, f_processed_sent2, f_labels


def transform_texts(batch_id, texts):
    nlp = spacy.load("en_core_web_lg", disable=['ner'])
    nlp.disable_pipes('ner')
    sentences = list(nlp.pipe(tqdm(texts, desc=f"Processing batch {batch_id} pipeline - {nlp.pipe_names}")))

    return sentences


def get_sentences_mulitprocess(data, batch_size, n_jobs):
    processed_sent1, processed_sent2, labels = [], [], []

    # process sent1
    sent_list1 = map(operator.itemgetter('sentence1'), tqdm(data, desc='Getting list of sentence1'))
    partitions1 = minibatch(sent_list1, size=batch_size)

    executor1 = Parallel(n_jobs=n_jobs, backend="multiprocessing", prefer="processes")

    do1 = delayed(partial(transform_texts))
    tasks1 = (do1(i, batch) for i, batch in enumerate(partitions1))
    processed_sent1 += executor1(tasks1)

    # process sent2
    sent_list2 = map(operator.itemgetter('sentence2'), tqdm(data, desc='Getting list of sentence2'))
    partitions2 = minibatch(sent_list2, size=batch_size)

    executor2 = Parallel(n_jobs=n_jobs, backend="multiprocessing", prefer="processes")

    do2 = delayed(partial(transform_texts))
    tasks2 = (do2(i, batch) for i, batch in enumerate(partitions2))
    processed_sent1 += executor2(tasks2)

    # process labels
    label = map(operator.itemgetter('gold_label'), tqdm(data, desc='Getting list of gold labels'))

    return processed_sent1, processed_sent2, labels
