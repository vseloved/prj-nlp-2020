import spacy
import re

nlp = spacy.load('en_core_web_md')


def sequence_length(sequence):
    length = 0
    for token in sequence:
        if token.pos_ != "PUNCT":
            length += len(token.text)
    return length


def sequence_to_text(sequence):
    text = ""
    for token in sequence:
        text += token.text
    return text


def capitalize_alpha(source):
    if source.isupper(): return source
    if source[0].isupper(): return source
    if source[0] in ["'", "\"", "("]:
        return source[:1] + source[1].capitalize() + source[2:]
    return source.capitalize()

def rule_no5(source, token):
    text = source
    if token.tag_ in ["TO", "DT", "IN", "CC", "UH", "RP"]:
        text = text.lower()
    return text


def isNoun(token):
    return token.tag_.startswith("NN")


def isVerb(token):
    return token.tag_.startswith("VB") or token.tag_ == "MD"

def isPronoun(token):
    return token.tag_.startswith("PRP") or token.tag_.startswith("WP")


def isAdjective(token):
    return token.tag_.startswith("JJ")


def isAdverb(token):
    return token.tag_.startswith("RB") or token.tag_ == "WRB"


def isSubConjunction(token):
    return token.pos_ == "SCONJ" and token.dep_ != "prep"


def apply_rules(source_text):
    headline_text = ""
    sequence = []
    doc = nlp(source_text)
    after_colon = False
    for tok in doc:
        sequence.append(tok)
        if tok.whitespace_:
            text = process_single_word(sequence, headline_text == "", False, after_colon)
            headline_text += text + " "
            sequence = []
            if text.endswith(":"):
                after_colon = True
            else:
                after_colon = False

    if len(sequence) > 0:
        text = process_single_word(sequence, False, True, after_colon)
        headline_text += text
    return headline_text


def process_single_word(sequence, isFirstWord, isLastWord, after_colon):
    token = get_text_token(sequence)

    text = sequence_to_text(sequence)
    text = rule_no5(text, token)

    # implementation of rule No1
    if sequence_length(sequence) > 3:
        text = capitalize_alpha(text)

    # implementation of rule No3
    if isNoun(token) or \
            isVerb(token) or \
            isPronoun(token) or \
            isAdjective(token) or \
            isAdverb(token) or \
            isSubConjunction(token):
        text = capitalize_alpha(text)
    if isFirstWord or isLastWord:
        text = capitalize_alpha(text)
    if after_colon:
        text = capitalize_alpha(text)

    # implementation of rule No5
    for m in re.finditer(r"-[a-z]", text):
        text = text[:m.end() - 1] + text[m.end() - 1].capitalize() + text[m.end():]
    return text


def get_text_token(sequence):
    for token in sequence:
        if token.pos_ != "PUNCT":
            return token
    return sequence[0]


def process_headline(source_text):
    headline_text = apply_rules(source_text)
    return headline_text