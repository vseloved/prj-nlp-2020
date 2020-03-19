from collections import Counter
import tokenize_uk
import pymorphy2
morph = pymorphy2.MorphAnalyzer(lang='uk')

def get_collocations(text):
    
    collocations = Counter()
    for i in range(1, len(text)):
        prev_word = text[i-1]
        word = text[i]
        if word.tag.POS == "NOUN" and word.tag.animacy == "anim" and prev_word.tag.POS == "ADJF":
            collocations[(prev_word.normal_form, word.normal_form)] += 1
    return collocations


with open("/home/dasha/Документы/курс/prj-nlp-2020/tasks/02-structural-linguistics/data/tyhrolovy.txt", "r") as f:
    text = f.read()
    words = tokenize_uk.tokenize_words(text)
    parsed = [morph.parse(word)[0] for word in words]
    
    collocations = get_collocations(parsed)
    for c, freq in sorted(collocations.items(), key=lambda x:x[1], reverse=True):       
        print('{0}: {1}'.format(freq, ' '.join(c)))
