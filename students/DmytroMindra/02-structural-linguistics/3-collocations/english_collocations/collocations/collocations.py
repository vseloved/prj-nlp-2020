import nltk
from nltk.corpus import wordnet as wordnet

nltk.download('wordnet')


def synonyms_to_speak():
    words = [('state.v.01', "say"),
             ("tell.v.02", "tell"),
             ("talk.v.02", "talk"),
             ("claim.v.01", "claim"),
             ("communicate.v.01", "communicate")]
    synonyms = set()
    for word in words:
        word_synsets = wordnet.synsets(word[1])
        original = wordnet.synset(word[0])
        for synonym in word_synsets:
            for l in synonym.lemmas():
                if l.name() not in synonyms:
                    if original.wup_similarity(synonym) > 0.5:
                        synonyms.add(l.name())
    return synonyms
