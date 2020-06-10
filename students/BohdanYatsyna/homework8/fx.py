NULL_TUPLE = ('NULL', 'NULL')

WORD = 0
POS = 1
HEAD = 2
LABEL = 3
LEMMA = 4


def head_children(arcs, h, sent):
    children = list(filter(lambda x: x[0] == h, arcs))
    if len(children):
        lc1 = min(d for (h, d) in children)
        rc1 = max(d for (h, d) in children)
        return sent[lc1], sent[rc1]
    return NULL_TUPLE, NULL_TUPLE

def ex(conf):
    sentence = conf.sentence
    features = {}

    #b0w = "NULL"
    b0p = "NULL"
    b10p = "NULL"
    #b1w = "NULL"
    b1p = "NULL"
    #b2w = "NULL"
    b2p = "NULL"
    #s0w = "NULL"
    s0p = "NULL"

    # lemma
    b0l = "NULL"
    b1l = "NULL"
    b2l = "NULL"
    s0l = "NULL"
    s1l = "NULL"

    #s1w = "NULL"
    s1p = "NULL"

    s10p = "NULL"
    sr0p = "NULL"
    sh0p = "NULL"
    heads = dict((arc[1], arc[0]) for arc in conf.arcs)

    if len(conf.buffer) > 0:
        b0_pos = conf.buffer[0]
        if b0_pos < len(sentence):
            #b0w = sentence[b0_pos][WORD]
            b0l = sentence[b0_pos][LEMMA]
            b0p = sentence[b0_pos][POS]
        else:
            #b0w = "ROOT"
            b0l = "ROOT"
            b0p = "ROOT"
        hc = head_children(conf.arcs, b0_pos, sentence)
        left_most = hc[0]
        b10p = left_most[POS]
        if len(conf.buffer) > 1:
            b1_pos = conf.buffer[1]
            if b1_pos < len(sentence):
                #b1w = sentence[b1_pos][WORD]
                b1l = sentence[b1_pos][LEMMA]
                b1p = sentence[b1_pos][POS]
            else:
                #b1w = "ROOT"
                b1l = "ROOT"
                b1p = "ROOT"
            if len(conf.buffer) > 2:
                b2_pos = conf.buffer[2]
                if b2_pos < len(sentence):
                    #b2w = sentence[b2_pos][WORD]
                    b2l = sentence[b2_pos][LEMMA]
                    b2p = sentence[b2_pos][POS]
                else:
                    #b2w = "ROOT"
                    b2l = "ROOT"
                    b2p = "ROOT"

    if len(conf.stack) > 0:
        s0_pos = conf.stack[-1]
        if s0_pos < len(sentence):
            #s0w = sentence[s0_pos][WORD]
            s0l = sentence[s0_pos][LEMMA]
            s0p = sentence[s0_pos][POS]
        else:
            #s0w = "ROOT"
            s0l = "ROOT"
            s0p = "ROOT"

        if len(conf.stack) > 1:
            s1_pos = conf.stack[-2]
            #s1w = sentence[s1_pos][WORD]
            s1l = sentence[s1_pos][LEMMA]
            s1p = sentence[s1_pos][POS]

        hc = head_children(conf.arcs, s0_pos, sentence)
        left_most = hc[0]
        s10p = left_most[POS]
        right_most = hc[1]
        sr0p = right_most[POS]

        sh0p = "NULL"
        if s0_pos in heads:
            sh0p = sentence[heads[s0_pos]][POS]

    #b0wp = b0w + "/" + b0p
    #b1wp = b1w + "/" + b1p
    #s0wp = s0w + "/" + s0p
    #s1wp = s1w + "/" + s1p
    #b2wp = b2w + "/" + b2p

    b0lp = b0l + "/" + b0p
    b1lp = b0l + "/" + b0p
    b2lp = b2l + "/" + b2p
    s0lp = s0l + "/" + s0p
    s1lp = s1l + "/" + s1p


    #features["s0wp=" + s0wp] = 1
    #features["s0w=" + s0w] = 1
    features["s0p=" + s0p] = 1
    #features["s1wp=" + s1wp] = 1
    #features["s1w=" + s1w] = 1
    features["s1p=" + s1p] = 1

    # lemma
    features["s0lp=" + s0lp] = 1
    features["s0l=" + s0p] = 1
    features["s1lp=" + s1lp] = 1
    features["s1l=" + s1l] = 1

    #features["b0wp=" + b0wp] = 1
    #features["b0w=" + b0w] = 1
    features["b0p=" + b0p] = 1
    #features["b1wp=" + b1wp] = 1
    #features["b1w=" + b1w] = 1
    features["b1p=" + b1p] = 1
    #features["b2wp=" + b2wp] = 1
    #features["b2w=" + b2w] = 1
    features["b2p=" + b2p] = 1

    # lemma
    features["b0lp=" + b0lp] = 1
    features["b0l=" + b0l] = 1
    features["b1lp=" + b1lp] = 1
    features["b1l=" + b1l] = 1
    features["b2lp=" + b2lp] = 1
    features["b2l=" + b2l] = 1

    #s0wp_b0wp = s0wp + ";" + b0wp
    #s0wp_b0w = s0wp + ";" + b0w
    #s0w_b0wp = s0w + ";" + b0wp
    #s0wp_b0p = s0wp + ";" + b0p
    #s0p_b0wp = s0p + ";" + b0wp
    #s0w_b0w = s0w + ";" + b0w
    s0p_b0p = s0p + ";" + b0p
    b0p_b1p = b0p + ";" + b1p

    # lemma
    s0lp_b0lp = s0lp + ";" + b0lp
    s0lp_b0l = s0lp + ";" + b0l
    s0l_b0lp = s0l + ";" + b0lp
    s0lp_b0p = s0lp + ";" + b0p
    s0p_b0lp = s0p + ";" + b0lp
    s0l_b0l = s0l + ";" + b0l

    #features["s0wp_b0wp=" + s0wp_b0wp] = 1
    #features["s0wp_b0w=" + s0wp_b0w] = 1
    #features["s0w_b0wp=" + s0w_b0wp] = 1
    #features["s0wp_b0p=" + s0wp_b0p] = 1
    #features["s0p_b0wp=" + s0p_b0wp] = 1
    #features["s0w_b0w=" + s0w_b0w] = 1
    features["s0p_b0p=" + s0p_b0p] = 1
    features["b0p_b1p" + b0p_b1p] = 1

    # lemma
    features["s0lp_b0lp=" + s0lp_b0lp] = 1
    features["s0lp_b0l=" + s0lp_b0l] = 1
    features["s0l_b0lp=" + s0l_b0lp] = 1
    features["s0lp_b0p=" + s0lp_b0p] = 1
    features["s0p_b0lp=" + s0p_b0lp] = 1
    features["s0l_b0l=" + s0l_b0l] = 1

    b0p_b1p_b2p = b0p + ";" + b1p + ";" + b2p
    s0p_b0p_b1p = s0p + ";" + b0p + ";" + b1p
    sh0p_s0p_b0p = sh0p + ";" + s0p + ";" + b0p
    s0p_s10p_b0p = s0p + ";" + s10p + ";" + b0p
    s0p_sr0p_b0p = s0p + ";" + sr0p + ";" + b0p
    s0p_b0p_b10p = s0p + ";" + b0p + ";" + b10p
    features["b0p_b1p_b2p=" + b0p_b1p_b2p] = 1
    features["s0p_b0p_b1p=" + s0p_b0p_b1p] = 1
    features["sh0p_s0p_b0p=" + sh0p_s0p_b0p] = 1
    features["s0p_s10p_b0p=" + s0p_s10p_b0p] = 1
    features["s0p_sr0p_b0p=" + s0p_sr0p_b0p] = 1
    features["s0p_b0p_b10p" + s0p_b0p_b10p] = 1

    return features