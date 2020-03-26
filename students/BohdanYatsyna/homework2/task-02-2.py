import spacy
from tqdm import tqdm
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('sentiwordnet')
nltk.download('wordnet')
nltk.download('vader_lexicon')

nlp = spacy.load("en_core_web_md")
sid = SentimentIntensityAnalyzer()

text_with_enteties  = ""
text_with_pos = ""

with open("../tasks/02-structural-linguistics/data/examiner-headlines.txt") as file:
    data = file.readlines()
statistic = {'entity':0, 'more lvl':0, 'most lvl':0, 'polarity':0}
for line in tqdm(data):
    have_entenies = False
    have_more_lvl = False
    have_most_lvl = False
    have_polarity = False
    doc = nlp(line)
    for token in doc:
        # enteties presence in token
        if token.ent_type_ == "PERSON" or token.ent_type_ == "ORG" or token.ent_type_ == "GPE"\
        or token.ent_type_ == "FAC" or token.ent_type_ == "EVENT" or token.ent_type_ == "PRODUCT":
            have_entenies = True

        # super ADV and ADG
        if token.pos_ == "ADJ" or token.pos_ == "ADV":
            # more lvl check
            if token.text[-2:] == "er":
                have_more_lvl = True
            if token.text.lower() == "worse" or token.text.lower() == "more" or token.text.lower() == "less":
                have_more_lvl = True


            # most lvl check
            if token.text[-3:] == "est":
                have_most_lvl = True
            if token.text.lower() == "worst" or token.text.lower() == "most" or token.text.lower() == "least":
                have_most_lvl = True

    # polarity
    ss = sid.polarity_scores(line)
    if ss['pos'] > 0.5 or ss['neg'] > 0.5:
        have_polarity = True

    if have_entenies: statistic['entity'] += 1
    if have_more_lvl: statistic['more lvl'] += 1
    if have_most_lvl: statistic['most lvl'] += 1
    if have_polarity: statistic['polarity'] += 1

with open('../students/BohdanYatsyna/homework2/task-02-2-statistic.txt', 'w') as f:
    print('examiner-headlines.txt - statistic entities: {:2.2%}, more lvl:{:2.2%}, most lvl: {:2.2%}, polarity: {:2.2%}'.\
          format(statistic['entity']/5000, statistic['more lvl']/5000,statistic['most lvl']/5000,statistic['polarity']/5000),file=f)