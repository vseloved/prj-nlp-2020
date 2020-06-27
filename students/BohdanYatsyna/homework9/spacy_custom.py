import spacy
from process import get_sentences, get_sentences_wo_try
from fileio import read_jsonnl
from spacy.tokens import Token

def add_negation(doc):
    neg_list = ['not', 'no', 'never', 'n\'t']
    perv_token_neg = None
    current_neg = None
    for token  in doc:
        if perv_token_neg is None or perv_token_neg is False:
            current_neg = token.text in neg_list
        else:
            current_neg = not (token.text in neg_list)

        token._.is_negative = current_neg
        perv_token_neg = current_neg
    return doc


# def print_doc(doc):
#     for token in doc:
#         print(''.join(f"{token.text}/{token.pos_}/{token._.is_negative}"))
# # testing spacy extention
# def main():
#     dev_data = read_jsonnl("snli_1.0/snli_1.0_dev.jsonl")
#     #nlp = setup_nlp()
#     Token.set_extension("is_negative", default=False)
#     nlp = spacy.load("en_core_web_lg", disable=['ner'])
#     nlp.add_pipe(add_negation)
#     print(nlp.pipe_names)
#
#     dev_processed_sent1, dev_processed_sent2, dev_labels = get_sentences_wo_try(nlp, dev_data, 10000, 1,
#                                                                          "Dev data -", "dev")
#     for i, doc in enumerate(dev_processed_sent1):
#         for j, token in enumerate(doc):
#             if token.text in ['not', 'no', 'never', 'n\'t']:
#                 print(" ")
#                 print("-----------------------------------------")
#                 print(f"doc-id:{i}   tok-id:{j} {doc}")
#                 print(f"text {token.text} / lemma {token.lemma_} / pos {token.pos_}")
#                 print("------------------------------------------")
#     #   doc-id:506   tok-id:17
#     #   doc-id:1304   tok-id:6
#     #   doc-id:2145   tok-id:2
#     print_doc(dev_processed_sent1[506])
#     print_doc(dev_processed_sent1[1304])
#     print_doc(dev_processed_sent1[2145])
#
#     t = 1
#
# if __name__ == '__main__':
#     main()
