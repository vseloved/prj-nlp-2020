import spacy
import json
from tqdm import tqdm

nlp = spacy.load("en_core_web_md")

modified_text  = ""

with open("../tasks/02-structural-linguistics/data/examiner-headlines.txt") as file:
    data = file.readline()

doc = nlp(data)
for token in doc:
    if token.ent_type_ != '':
        modified_text += token.text + '/'+ token.ent_type_ + token.whitespace_
    else:
        modified_text += token.text + token.whitespace_

print(modified_text)
# for i, d in tqdm(enumerate(data)):
#