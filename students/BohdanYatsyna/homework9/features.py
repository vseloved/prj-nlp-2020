
def exctract_features(text_sent_tokens, hypothesis_sent_tokens, updaters):
    features = {}

    features['text-hyp-sim'] = get_jaccard_sim_by_lemma(text_sent_tokens, hypothesis_sent_tokens)
    text_hyp_sim_verb = get_jaccard_sim_by_verb(text_sent_tokens, hypothesis_sent_tokens)
    if text_hyp_sim_verb:
        features['text-hyp-sim-verb'] = text_hyp_sim_verb

    features['text-len'] = len(text_sent_tokens)
    features['hyp-len'] = len(hypothesis_sent_tokens)

    for updater in updaters:
        updater(features, text_sent_tokens, hypothesis_sent_tokens)

    return features