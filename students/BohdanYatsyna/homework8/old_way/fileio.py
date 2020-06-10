from conllu import parse


def read_conll_deps(f):
    with open(f, "r") as f:
        readed_trees = parse(f.read())
    return readed_trees
