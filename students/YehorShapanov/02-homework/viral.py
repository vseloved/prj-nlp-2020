import nltk 
import spacy 
from nltk.corpus import sentiwordnet as swn
from nltk.stem.porter import *
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups

nlp = spacy.load("en_core_web_md")
stemmer = PorterStemmer()
def penn_to_c(tag):
    if tag=="ADJ":
        return tag
    if tag=="ADV":
        return tag
    if tag.startswith('J'):
        return "ADJ"
    elif tag.startswith('N'):
        return "NOUN"
    elif tag.startswith('R'):
        return "ADV"
    elif tag.startswith('V'):
        return "VERB"
    return None

def get_sentiment(word,pos):
    _tag = penn_to_c(pos)
    if _tag not in ("NOUN", "ADJ", "ADV"):
        return -1

    synsets = list(swn.senti_synsets(word))
    if not synsets:
        return -1

    # Take the first sense, the most common
    synset = synsets[0]
    positive = synset.pos_score()
    negative = synset.neg_score()
    return positive-negative

def has_comparatives(doc):
    for token in doc:
        if token.ent_type_ == '':
            if token.pos_=="ADJ" and (token.tag_=="JJR" or token.tag_=="JJS"):
                return True
            if token.pos_=="ADV" and (token.tag_=="RBR" or token.tag_=="RBS"):
                return True
    return False

def validate_sentense(s):
    doc = nlp(s)
    sentiments = []
    for token in doc:
        if token.ent_type_ == '':
            sentiments.append(get_sentiment(token.lemma_, token.pos_))
    score = 0
    for a in sentiments:
        if a != -1:
            score += a
    has_named_entities = len(doc.ents)>0
    is_positive_or_negative = score>0.5 or score<-0.5
    has_degrees_of_comparison = has_comparatives(doc)
    return [has_named_entities, is_positive_or_negative, has_degrees_of_comparison]


validation_set = list()
with open('examiner-headlines.txt') as file:
    validation_set = file.readlines()

result = []
equal_three = 0
equal_two = 0
at_leas_one = 0

for s in validation_set:
    val_res = validate_sentense(s)
    result.append(sum(val_res))

equal_three = result.count(3)
equal_two = result.count(2)
at_leas_one = result.count(1)

print("3: {}, 2: {}, 1: {}".format(equal_three, equal_two, at_leas_one))