import json
    # nlp.tokenizer.add_special_case(u'go-to',
    # [
    #     {
    #         "ORTH": u'go-to',
    #         "LEMMA": u'go-to',
    #         "POS": u'NOUN'
    #     }
    # ])
import re
import spacy

nlp = spacy.load('en_core_web_md')

def my_nlp(s):
    # don't split on '-'       
    infixeslist = ['\\.\\.+', '…']
    infixes_regex = spacy.util.compile_infix_regex(infixeslist)
    nlp.tokenizer.infix_finditer = infixes_regex.finditer
    # don't split on apostrophe
    new_rules = {key: value for key, value in nlp.tokenizer.rules.items() if "'" not in key and "’" not in key and "‘" not in key}
    # don't tokenize 's 

    nlp.tokenizer.rules = new_rules
    tok_exp = nlp.tokenizer.explain(s)
    suffix_idx = []
    prefix_idx = []
    for i, t in enumerate(tok_exp):
        if t[0]=="SUFFIX":
            suffix_idx.append(i)
        if t[0]=="PREFIX":
            prefix_idx.append(i)

    doc = nlp(s)
    token_merge_idxs = []
    for idx in suffix_idx:
        t = doc[idx]
        token_merge_idxs.append({"nbor":t.nbor(-1).idx, "idx":t.idx, "len":len(t.text)})

    for idx in prefix_idx:
        t = doc[idx]
        if t == doc[-1]: #last token
            token_merge_idxs.append({"nbor":t.idx, "idx":t.idx, "len":len(t.text)})
        else:
            token_merge_idxs.append({"nbor":t.idx, "idx":t.nbor(1).idx, "len":len(t.nbor(1).text)})
    
    for o in token_merge_idxs:
        l = o["nbor"]
        r = o["idx"]+o["len"]
        doc.merge(l, r)

    return doc


def test_upper(w):
    count = 0
    starts_with_upper = False
    for (i, c) in enumerate(w): 
        if c.isupper():
            if i==0: starts_with_upper = True
            else:
                if not starts_with_upper: return True
            count += 1
            if count > 1: return True
    return False

def capitalize(w):
    if w in noncapitalizable_cases: return w
    result = ""
    for (i,x) in enumerate(w):
        if i==0 and x.isdigit(): return w
        if x.isalpha():
            result+=x.capitalize()
            result+=w[i+1:]
            return result
        else:
            result+=x
    return result


capitalize_locations = {
    "sf": "SF"
}

noncapitalizable_cases = {"the"}
rules = {"NOUN","PRON","VERB","ADJ","ADV","AUX"}
tags = {"PRP$","RB"}

def process_token(t, last_token):
    text = t.text
    if t.ent_type_=='LOC':
        if text in capitalize_locations:
            return (t, capitalize_locations[text])
        else:
           return (t, text.capitalize())

    a = text.split('-')
    if len(a) >= 2:
        return (t, "-".join([x.capitalize() for x in a]))
    process = len(text) >= 4 or last_token or t.is_sent_start or (t.pos_ in rules) or (t.tag_ in tags)
    if t.dep_=="appos" or t.dep_=="nummod":
        process = True
    if t.pos_=="SCONJ" and t.dep_=="mark":
        process = True

    if process:
        if test_upper(text):
            return (t, text)
        else:
            return (t, capitalize(text))
    else:
        return (t, text)

def process_sentence(s):
    tmp = my_nlp(s)
    l = []
    for x in tmp:
        t = x.text
        if not t.isupper or x.pos_ == "ADP" or x.pos_ == "PART" or len(t)==1:
            l.append(t.lower())
        else:
            l.append(t)

    s = my_nlp(" ".join(l))
    p = [process_token(token, i == len(s)-1) for i, token in enumerate(s)]
    result = []
    opened_strophe = False
    prev_pos=""
    for t in p: 
        text = t[1]
        tag = t[0].tag_
        pos = t[0].pos_

        if text=="'" and len(result)==0:
            prev_pos="PUNCT"
            result.append(text)
            continue

        if prev_pos=='PUNCT' and tag=='POS' and len(result)>1:
            s2 = result.pop()
            s1 = result.pop()
            result.append(s1+s2+text)
            prev_pos=""
            continue

        if text=="'" and opened_strophe:
            opened_strophe = not opened_strophe
            prev = result.pop()
            result.append(prev + text)
            continue

        if opened_strophe:
            prev = result[-1]
            if prev == "'":
                prev = result.pop()
                result.append(prev + text)
                continue

        #hardcode
        if text[0]=="'" and len(text)>1 and text[1]==" ":
            prev = result.pop()
            new = prev + text
            result.append(new)
            continue

        if ((pos == "PUNCT" and (text != "'" and text != "-")) or tag == "POS") and len(text)==1 and len(result)>0:
            prev = result.pop()
            new = prev + text
            result.append(new)
        else:
            if len(result)>0:
                if result[-1]=="'":
                    new = result.pop() + text
                    result.append(new)
                    continue
            result.append(text)
        prev_pos = pos
        if text == "'":
            opened_strophe = not opened_strophe
    return " ".join(result)

def validate(val_set):
    count = 0
    failed = 0
    for l in val_set: 
        s = l.strip()
        print("Count: ", count)
        print(s)
        count += 1
        if s != process_sentence(s):
            failed += 1
    print("count: {}, failed: {}".format(count, failed))


validation_set = list()
with open('examiner-headlines.txt') as file:
    validation_set = file.readlines()

# print(process_sentence("Want to be in 'The Mortal Instruments: City of Ashes?'"))

# def validate(val_set):
#     for i, case in enumerate(val_set):
#         res = process_sentence(case[0]) == case[1]
#         if not res:
#             print(str(i) + " " + str(res))


# validation_set = dict()
# with open('headlines-test-set.json') as json_file:
#     validation_set = json.load(json_file)


validate(validation_set)
