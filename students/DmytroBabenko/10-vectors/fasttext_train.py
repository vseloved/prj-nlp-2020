import gensim
import pandas as pd
from gensim.models.word2vec import LineSentence
from scipy import spatial


from ast import literal_eval

if __name__ == "__main__":
    df_train_corpus = pd.read_csv('data/train-tokens.csv')

    corpus = [literal_eval(item) for item in df_train_corpus['tokens'].values]

    initial_model_path = "/home/dbabenko/Downloads/cc.uk.300.bin"
    ft_model = gensim.models.fasttext.load_facebook_model(initial_model_path)

    # corpus_file = "data/1551-uk-corpus.txt"
    # line_sentences = LineSentence(corpus_file)
    ft_model.build_vocab(corpus, update=True)
    ft_model.train(corpus, total_examples=len(corpus), epochs=1)

    ft_model.save('data/1551.cc.uk.300.bin')


    a = 10






