def exctract(sent1, sent2):
    features = {}

    # processed_tokens_sent1 = []
    # for tok in sent1:
    #     tok.
    #     processed_tokens_sent1.append()
    # tokens_sent1
    features['sim-lemma'] = similarity_lemma(sent1, sent2)
    features['sim-verb'] = similaity_verb(sent1, sent2)

    # if text_hyp_sim_verb:
    #     features['text-hyp-sim-verb'] = text_hyp_sim_verb

    # features['text-len'] = len(text_sent_tokens)
    # features['hyp-len'] = len(hypothesis_sent_tokens)

    return features


def similarity_lemma(sent1, sent2):
    ## added removing stop words (if not token.is_stop)
    lemmas1 = set([token.lemma_ for token in sent1 if not token.is_stop])
    lemmas2 = set([token.lemma_ for token in sent2 if not token.is_stop])

    matched = lemmas1.intersection(lemmas2)

    if len(lemmas1) + len(lemmas2) - len(matched) == 0:
        return "NULL"

    return float(len(matched)) / (len(lemmas1) + len(lemmas2) - len(matched))


def similaity_verb(sent1, sent2):
    verbs1 = set(
        [token.lemma_ for token in sent1 if token.pos_ == "VERB" and not token.lemma == "be" and not token.is_stop])
    verbs2 = set(
        [token.lemma_ for token in sent2 if token.pos_ == "VERB" and not token.lemma == "be" and not token.is_stop])

    matched = verbs1.intersection(verbs2)

    if len(verbs1) + len(verbs2) - len(matched) == 0:
        return "NULL"

    return float(len(matched)) / (len(verbs1) + len(verbs2) - len(matched))
