import string
import nltk
from nltk.tokenize import TweetTokenizer, word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.corpus import stopwords, wordnet as wn, sentiwordnet as swn
from nltk import ne_chunk

stop_words = stopwords.words('english')
tknzr = TweetTokenizer()
lemmatizer = WordNetLemmatizer()


def get_sentiment(t_toks):
    positive = 0
    negative = 0
    
    for word, tag in t_toks:
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
    
        synsets =  wn.synsets(lemmatizer.lemmatize(word, pos), pos=pos)
        if synsets:
            synset = synsets[0]      #the most common sense
            swn_synset = swn.senti_synset(synset.name())

            positive += swn_synset.pos_score()
            negative += swn_synset.neg_score()
    
    final_sentiment = positive - negative

    if final_sentiment >= 0.2 or final_sentiment <= -0.2:
        return 1
    
    
def comparative_superlative(t_toks):
    for word, tag in t_toks:
        if tag in ["JJR", "JJS", "RBR", "RBS"]:
            return 1
        
def find_ne(t_toks):
    ne = ne_chunk(t_toks, binary=True)
    for subtree in ne.subtrees(filter=lambda x: x.label() == 'NE'):
        if subtree.leaves():
            return 1
    
    
    
if __name__ == '__main__':
    
    count_lines = 0
    sents_with_ne = 0
    sents_with_comp_super = 0
    sents_with_sentiment = 0

    with open('/home/dasha/Документы/курс/prj-nlp-2020/tasks/02-structural-linguistics/data/examiner-headlines.txt', 'r') as f:
        lines = f.readlines()

        for i, line in enumerate(lines):
            count_lines += 1

            tokens = tknzr.tokenize(line)
            cleaned_tokens = [t for t in tokens if t not in string.punctuation] #and t.lower() not in stop_words]
            tagged_tokens = pos_tag(cleaned_tokens)

            if comparative_superlative(tagged_tokens) == 1:
                sents_with_comp_super += 1
            if find_ne(tagged_tokens) == 1:
                sents_with_ne += 1
            if get_sentiment(tagged_tokens) == 1:
                sents_with_sentiment += 1

    print('Sentences with Named Entities: {0}%\nSentences with sentiment: {1}%\nSentences with Adjectives/Adverbs: {2}%'.format((sents_with_ne/count_lines)*100, round((sents_with_sentiment/count_lines)*100, 2), (sents_with_comp_super/count_lines)*100))
    
>>> Sentences with Named Entities: 79.64%  
>>> Sentences with sentiment: 45.3%  
>>> Sentences with Adjectives/Adverbs: 4.06%
