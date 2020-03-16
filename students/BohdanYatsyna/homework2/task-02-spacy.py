import spacy
import en_core_web_sm

nlp = spacy.load("en_core_web_sm")

text = "Don't stop me now"

print(text)

for i in range(len(text)):
    if len(text[i])>3:
        text[i] = text[i].capitalize()

print(text)

