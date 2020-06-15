
def exctract(sent1, sent2):
    features = {}

    features['similarity-lemma'] = similarity_lemma(sent1, sent2)
    #text_hyp_sim_verb = get_jaccard_sim_by_verb(sent1, sent2)
    # if text_hyp_sim_verb:
    #     features['text-hyp-sim-verb'] = text_hyp_sim_verb

    # features['text-len'] = len(text_sent_tokens)
    # features['hyp-len'] = len(hypothesis_sent_tokens)

    return features

def similarity_lemma(sent1, sent2):
    lemmas1 = set([token.lemma_ for token in sent1])
    lemmas2 = set([token.lemma_ for token in sent2])

    matched = lemmas1.intersection(lemmas2)
    return float(len(matched)) / (len(lemmas1) + len(lemmas2) - len(matched))