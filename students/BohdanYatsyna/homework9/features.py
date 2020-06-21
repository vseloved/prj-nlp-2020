from jiwer import wer
from nltk.corpus import wordnet
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import single_meteor_score
from rouge import Rouge
from spacy.symbols import VERB, PROPN, NOUN, ADJ, ADV


def exctract(sent1, sent2, config):
    lemmas1 = [token.lemma_ for token in sent1 if not token.is_stop and not token.is_punct]
    lemmas2 = [token.lemma_ for token in sent2 if not token.is_stop and not token.is_punct]

    lemmas_pos_neg1 = set(
        [(token.lemma_, token.pos, token._.is_negative) for token in sent1 if not token.is_stop and not token.is_punct])
    lemmas_pos_neg2 = set(
        [(token.lemma_, token.pos, token._.is_negative) for token in sent2 if not token.is_stop and not token.is_punct])
    features = {}

    # lemma + pos + negated coverage treshhold
    features['lemma-coverage-threshold'] = lemma_coverage_treshold(lemmas_pos_neg1, lemmas_pos_neg2)
    if config.f_lemma_verb:
        features['lemma-verb-coverage-threshold'] = lemma_coverage_treshold(lemmas_pos_neg1, lemmas_pos_neg2, [VERB])
    if config.f_lemma_noun:
        features['lemma-noun-coverage-threshold'] = lemma_coverage_treshold(lemmas_pos_neg1, lemmas_pos_neg2,
                                                                            [PROPN, NOUN])
    if config.f_lemma_adj:
        features['lemma-adj-coverage-threshold'] = lemma_coverage_treshold(lemmas_pos_neg1, lemmas_pos_neg2, [ADJ])
    if config.f_lemma_adv:
        features['lemma-adv-coverage-threshold'] = lemma_coverage_treshold(lemmas_pos_neg1, lemmas_pos_neg2, [ADV])
    # noun phrases coverage treshhold uni/bi/tri gramm coverage treshhold
    if config.f_noun_prases:
        features['noun-phrses-coverage-threshold'] = noun_phrase_coverage(sent1, sent2)
    # ner coverage treshold
    if config.f_ner:
        features['ner-coverage-threshold'] = ner_coverage(sent1, sent2)

    # BLEU festures
    if config.f_bleu_avg:
        features['bleu-avg'] = bleu_calculation(lemmas1, lemmas2)
    if config.f_bleu_1:
        features['bleu1'] = bleu_calculation(lemmas1, lemmas2, weights=(1, 0, 0, 0))
    if config.f_bleu_2:
        features['bleu2'] = bleu_calculation(lemmas1, lemmas2, weights=(0, 1, 0, 0))
    if config.f_bleu_3:
        features['bleu3'] = bleu_calculation(lemmas1, lemmas2, weights=(0, 0, 1, 0))
    if config.f_bleu_4:
        features['bleu4'] = bleu_calculation(lemmas1, lemmas2, weights=(0, 0, 0, 1))

    # Rouge
    rouge_score = rouge_calc(lemmas1, lemmas2)
    if config.f_rouge1:
        features['rouge-1-f'] = rouge_score['rouge-1']['f']
        features['rouge-1-p'] = rouge_score['rouge-1']['p']
        features['rouge-1-r'] = rouge_score['rouge-1']['r']
    if config.f_rouge2:
        features['rouge-2-f'] = rouge_score['rouge-2']['f']
        features['rouge-2-p'] = rouge_score['rouge-2']['p']
        features['rouge-2-r'] = rouge_score['rouge-2']['r']
    if config.f_rougel:
        features['rouge-l-f'] = rouge_score['rouge-l']['f']
        features['rouge-l-p'] = rouge_score['rouge-l']['p']
        features['rouge-l-r'] = rouge_score['rouge-l']['r']
    # Word accuracy
    if config.f_wer:
        features['1-wer'] = 1 - wer_calc(lemmas1, lemmas2)
    # meteor
    # features['meteor'] = meteor_calc(lemmas1, lemmas2)
    # synonyms
    if config.f_sim_lema:
        features['sim-lemma'] = similarity_lemma(lemmas_pos_neg1, lemmas_pos_neg2)
    if config.f_sim_verb:
        features['sim-verb'] = similaity_verb(sent1, sent2)
    if config.f_len_sent1:
        features['text-len'] = len(sent1)
    if config.f_len_sent2:
        features['hyp-len'] = len(sent2)

    # synonyms
    if config.f_syn:
        features['synonyms'] = get_synonyms_coverage_treshold(lemmas_pos_neg1, lemmas_pos_neg2)

    return features


def get_synonyms_coverage_treshold(lemmas_pos_neg1, lemmas_pos_neg2):
    syn_lemmas1, syn_lemmas2 = [], []
    for l in lemmas_pos_neg1:
        syn, ant = get_synonyms_and_antonyms(l)
        if l[2] is False:
            syn_lemmas1.extend(syn)
        else:
            syn_lemmas2.extend(ant)

    for l in lemmas_pos_neg2:
        syn, ant = get_synonyms_and_antonyms(l)
        if l[2] is False:
            syn_lemmas2.extend(syn)
        else:
            syn_lemmas1.extend(ant)

    return lemma_coverage_treshold(set(syn_lemmas1), set(syn_lemmas2))


def get_synonyms_and_antonyms(word):
    synonyms = []
    antonyms = []

    pos = {PROPN: wordnet.NOUN, NOUN: wordnet.NOUN, VERB: wordnet.VERB, ADJ: wordnet.ADJ, ADV: wordnet.ADV}

    if word[1] in pos:
        for syn in wordnet.synsets(word[0], pos=pos[word[1]]):
            try:
                for l in syn.lemmas():
                    synonyms.append(l.name())
                    if l.antonyms():
                        antonyms.append(l.antonyms()[0].name())
            except:
                continue

    return set(synonyms), set(antonyms)


def meteor_calc(lemmas1, lemmas2):
    if len(lemmas1) == 0 or len(lemmas2) == 0: return 0
    return single_meteor_score(" ".join(lemmas1), " ".join(lemmas2))


def wer_calc(lemmas1, lemmas2):
    if len(lemmas1) == 0 or len(lemmas2) == 0: return 0
    return 1 - wer(" ".join(lemmas1), " ".join(lemmas2))


def rouge_calc(lemmas1, lemmas2):
    try:
        rouge_scores = Rouge().get_scores(hyps=" ".join(lemmas1), refs=" ".join(lemmas2))[0]
    except:
        rouge_scores = {'rouge-1': {'f': 0, 'p': 0, 'r': 0},
                        'rouge-2': {'f': 0, 'p': 0, 'r': 0},
                        'rouge-l': {'f': 0, 'p': 0, 'r': 0}}

    finally:
        return rouge_scores


def bleu_calculation(lemmas1, lemmas2, weights=(0.25, 0.25, 0.25, 0.25)):
    bleu_rank = 0
    if len(lemmas1) == 0 or len(lemmas2) == 0: return 0

    try:
        bleu_rank = sentence_bleu(lemmas1, lemmas2, weights)
    except:
        bleu_rank = 0

    return bleu_rank


def ner_coverage(sent1, sent2):
    entities1 = set([ent.orth_ for ent in sent1.ents])
    entities2 = set([ent.orth_ for ent in sent2.ents])
    matched = entities1.intersection(entities2)

    if len(entities2) == 0:
        return 0
    else:
        return len(matched) / len(entities2)


def noun_phrase_coverage(sent1, sent2):
    noun_chunks1 = set([chunk.orth_ for chunk in sent1.noun_chunks])
    noun_chunks2 = set([chunk.orth_ for chunk in sent2.noun_chunks])
    matched = noun_chunks1.intersection(noun_chunks2)

    if len(noun_chunks2) == 0:
        return 0
    else:
        return len(matched) / len(noun_chunks2)


def lemma_coverage_treshold(lemmas_pos_neg1, lemmas_pos_neg2, filter=""):
    if filter != "":
        lemmas_pos_neg1 = token_filter(lemmas_pos_neg1, filter)
        lemmas_pos_neg2 = token_filter(lemmas_pos_neg2, filter)

    matched = lemmas_pos_neg1.intersection(lemmas_pos_neg2)

    if len(lemmas_pos_neg2) == 0:
        return 0
    else:
        return len(matched) / len(lemmas_pos_neg2)


def token_filter(token_set, filter):
    filtered = {tok for tok in token_set if tok[1] in filter}
    if filter == [VERB]:
        filtered = {tok for tok in filtered if tok[0] != "be"}
    return filtered


def similarity_lemma(lemmas_pos_neg1, lemmas_pos_neg2):
    ## added removing stop words (if not token.is_stop)

    matched = lemmas_pos_neg1.intersection(lemmas_pos_neg2)

    if len(lemmas_pos_neg1) + len(lemmas_pos_neg2) - len(matched) == 0:
        return "NULL"

    return float(len(matched)) / (len(lemmas_pos_neg1) + len(lemmas_pos_neg2) - len(matched))


def similaity_verb(sent1, sent2):
    verbs1 = set(
        [(token.lemma_, token.pos, token._.is_negative) for token in sent1 if
         token.pos_ == "VERB" and not token.lemma_ == "be" and not token.is_stop and not token.is_punct])
    verbs2 = set(
        [(token.lemma_, token.pos, token._.is_negative) for token in sent2 if
         token.pos_ == "VERB" and not token.lemma_ == "be" and not token.is_stop and not token.is_punct])

    matched = verbs1.intersection(verbs2)

    if len(verbs1) + len(verbs2) - len(matched) == 0:
        return "NULL"

    return float(len(matched)) / (len(verbs1) + len(verbs2) - len(matched))
