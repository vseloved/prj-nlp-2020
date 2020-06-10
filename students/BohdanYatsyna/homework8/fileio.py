from conllu import parse

def read_conll_deps(f):
    sentences = []
    with open(f, "r") as f:
        readed_trees = parse(f.read())

    for tree in readed_trees:
        tree = [t for t in tree if type(t["id"]) == int]
        sentence = []
        for token in tree:
            if token['head'] -1 == -1:
                sentence.append((token['form'].lower(),token['upos'], len(tree), token['deprel']))
            else:
                sentence.append((token['form'].lower(),token['upos'], token['head'] -1, token['deprel']))
        sentences.append(sentence)
    return sentences
