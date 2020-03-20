import spacy

nlp = spacy.load('en_core_web_md')

verbs = [
    "say", 
    "tell", 
    "speak", 
    "claim", 
    "communicate", 
    "contact", 
    "interact", 
    "chat", 
    "utter", 
    "converse",
    "narrate"
]

def collect_stat(text, result_dict):
    doc = nlp(text)
    for token in doc:
        if (token.pos_ == "VERB" or token.tag_ in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"])\
            and (token.text in verbs or token.lemma_ in verbs):
            # print("???? parent verb:", token)
            parent_verb = token
            if result_dict.get(parent_verb.lemma_) is None:
                result_dict[parent_verb.lemma_] = {}
            for t in doc:
                if t.pos_ == "ADV" and t.text.endswith("ly") and t.head == parent_verb:
                    if result_dict[parent_verb.lemma_].get(t.text) is None:
                        result_dict[parent_verb.lemma_][t.text] = 1
                    else:
                        result_dict[parent_verb.lemma_][t.text] += 1

                    # print("######")
                    # print(doc)
                    # print("$$$HEAD: ",t.head)
    return result_dict

            

if __name__ == "__main__":
    with open('data/blog2008.txt','r') as f:
        result_dict = {}
        for line in f:
            result_dict = collect_stat(line, result_dict)
        print(result_dict)