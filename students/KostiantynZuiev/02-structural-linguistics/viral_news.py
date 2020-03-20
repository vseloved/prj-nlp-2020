import spacy
import re
from nltk.corpus import sentiwordnet as swn

# ORG, MONEY, PERSON, GPE, LOC
nlp = spacy.load('en_core_web_md')

def examine_headline(text):
    doc = nlp(text)
    # print(text)
    # print("NER: ",check_ne(doc))
    # print("Sentiment: ",check_sentiment(doc))
    # print("Comp/Sup: ",check_pos(doc))
    return check_ne(doc), check_sentiment(doc), check_pos(doc)

def check_ne(doc):
    for ent in doc.ents:
        if ent.label_ in ('ORG', 'MONEY', 'PERSON', 'GPE', 'LOC'):
            # print(doc.ents)

            return 1
    
    return 0

def check_sentiment(doc):
    for token in doc:
        senti_texts = list(swn.senti_synsets(token.text))
        if senti_texts:
            if any([
                sum([st.pos_score() for st in senti_texts[:5]])/len(senti_texts[:5]) > 0.5,
                sum([st.neg_score() for st in senti_texts[:5]])/len(senti_texts[:5]) > 0.5,
            ]):

                return 1
    
    return 0

def check_pos(doc):
    for token in doc:
        if token.tag_ in ["JJS","JJR","RBS","RBR"]:
            
            return 1
    
    return 0


if __name__ == "__main__":
    with open('data/examiner-headlines.txt', 'r') as f:
        total = 0
        ner_checks, senti_checks, pos_checks = 0, 0, 0
        for line in f:
            ner_check, senti_check, pos_check = examine_headline(line)
            ner_checks += ner_check
            senti_checks += senti_check
            pos_checks += pos_check
            total += 1
        
        print(f'NER: {ner_checks/total*100}%, Sentiment: {senti_checks/total*100}%, POS: {pos_checks/total*100}%')
