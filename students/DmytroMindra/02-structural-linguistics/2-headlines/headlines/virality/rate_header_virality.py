import nltk
import spacy
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wordnet
nltk.download('wordnet')
nltk.download('sentiwordnet')

# model = 'en_core_web_sm'
model = 'en_core_web_md'

nlp = spacy.load(model)


def rate_virality(source_text):
    doc = parse_document(source_text)


def parse_document(source_text):
    return nlp(source_text)


def contains_named_entity(doc):
    for token in doc:
        # token.ent_iob_
        if token.ent_type_ in ["PERSON", "ORG"]:
            return True
    return False


def contains_comparative_or_superlative(doc):
    for token in doc:
        if token.tag_ in ["JJR", "JJS", "RBR", "RBS"]:
            return True
    return False


def contains_sentiment(doc):
    pass


def wordnet_pos_code(tag):
    if tag.startswith('NN'):
        return wordnet.NOUN
    elif tag.startswith('VB'):
        return wordnet.VERB
    elif tag.startswith('JJ'):
        return wordnet.ADJ
    elif tag.startswith('RB'):
        return wordnet.ADV
    else:
        return ''


def word_sense_cdf(word, context, wn_pos):
    senses = wordnet.synsets(word, wn_pos)
    if len(senses) > 0:
        cfd = nltk.ConditionalFreqDist((sense, def_word)
                                       for sense in senses
                                       for def_word in sense.definition().split()
                                       if def_word in context)
        best_sense = senses[0]
        for sense in senses:
            try:
                if cfd[sense].max() > cfd[best_sense].max():
                    best_sense = sense
            except:
                pass
        return best_sense
    else:
        return None


# taken from https://programtalk.com/vs2/?source=python/11823/yenlp/sentiwordnet.py
def sentence_score(text, doc, threshold=0.75, wsd=word_sense_cdf):
    obj_score = 0  # object score
    pos_score = 0  # positive score
    neg_score = 0  # negative score
    pos_score_thr = 0
    neg_score_thr = 0

    for token in doc:

        if token.tag_ != "PUNKT":
            sense = wsd(token.text, text, wordnet_pos_code(token.tag_))
            if sense is not None:
                sent = swn.senti_synset(sense.name())
                if sent is not None and sent.obj_score() != 1:
                    obj_score = obj_score + float(sent.obj_score())
                    pos_score = pos_score + float(sent.pos_score())
                    neg_score = neg_score + float(sent.neg_score())
                    if sent.obj_score() < threshold:
                        pos_score_thr = pos_score_thr + float(sent.pos_score())
                        neg_score_thr = neg_score_thr + float(sent.neg_score())

    return (pos_score - neg_score, pos_score_thr - neg_score_thr)
