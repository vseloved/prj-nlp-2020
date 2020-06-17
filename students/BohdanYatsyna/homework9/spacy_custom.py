import spacy
from spacy.tokens import Token

def setup_nlp():
    Token.set_extension("is_negative", default=False)

def add_negation(doc):
    perv_token_is_neg = False
    for token  in doc:

        token.is_negative