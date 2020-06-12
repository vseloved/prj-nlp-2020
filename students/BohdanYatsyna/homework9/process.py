import operator
from tqdm import tqdm
from spacy.util import minibatch
from joblib import Parallel, delayed
from functools import partial
import spacy


def get_sentences(nlp, data, batch_size, n_jobs, label):
    sent_list1 = map(operator.itemgetter('sentence1'), tqdm(data, desc=f'{label} Getting list of sentence1'))
    processed_sent1 = list(nlp.pipe(sent_list1, n_process=n_jobs, batch_size=batch_size))

    sent_list2 = map(operator.itemgetter('sentence2'), tqdm(data, desc=f'{label} Getting list of sentence2'))
    processed_sent2 = list(nlp.pipe(sent_list2, n_process=n_jobs, batch_size=batch_size))

    labels = map(operator.itemgetter('gold_label'), tqdm(data,desc=f'{label} Getting list of gold labels'))
    return processed_sent1, processed_sent2, labels


def transform_texts( batch_id, texts):

    nlp = spacy.load("en_core_web_lg", disable=['ner'])
    nlp.disable_pipes('ner')
    sentences = list(nlp.pipe(tqdm(texts, desc=f"Processing batch {batch_id} pipeline - {nlp.pipe_names}")))

    return sentences

def get_sentences1(data, batch_size, n_jobs):
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
    label = map(operator.itemgetter('gold_label'), tqdm(data,desc='Getting list of gold labels'))

    return processed_sent1, processed_sent2, labels