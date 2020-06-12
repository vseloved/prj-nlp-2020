from students.BohdanYatsyna.homework9.fileio import read_jsonnl
from students.BohdanYatsyna.homework9.process import get_sentences
import argparse
from datetime import datetime
import spacy

from sklearn.pipeline import Pipeline
from sklearn import svm
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Textual entalailment trainer")
    parser.add_argument('--batch_size', help='Batch size (default=1000)', default=10000)
    parser.add_argument('--train_file', help='Train file location ', default="snli_1.0/snli_1.0_train.jsonl")
    parser.add_argument('--dev_file', help='Train file location ', default="snli_1.0/snli_1.0_dev.jsonl")
    parser.add_argument('--test_file', help='Train file location ', default="snli_1.0/snli_1.0_test.jsonl")
    parser.add_argument('--proba', help='If True - app work as sample on cutted data', default=False)
    parser.add_argument('--n_jobs', help='Number of workers (default=1) use all cores', default=1)

    nlp = spacy.load("en_core_web_lg", disable=['ner'])

    opts = parser.parse_args()

    # measure execution time
    start_time = datetime.now()

    train_data = read_jsonnl(opts.train_file)
    dev_data = read_jsonnl(opts.dev_file)
    test_data = read_jsonnl(opts.test_file)

    if opts.proba:
        train_data = train_data[:100000]
        dev_data = dev_data[:2000]
        test_data = test_data[:2000]
    train_processed_sent1, train_processed_sent2, train_labels = get_sentences(nlp,train_data, opts.batch_size, opts.n_jobs, "Train data -")
    dev_processed_sent1, dev_processed_sent2, dev_labels = get_sentences(nlp,dev_data, opts.batch_size, opts.n_jobs, "Dev data -")
    test_processed_sent1, test_processed_sent2, test_labels = get_sentences(nlp,test_data, opts.batch_size, opts.n_jobs, "Test data -")


    # do your work here
    end_time = datetime.now()
    print('\n\nDuration: {}\n\n'.format(end_time - start_time))




