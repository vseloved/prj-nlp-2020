import sys
from collections import defaultdict
import stanza

def featdict(word):
    if word and word.feats:
        return dict(feat.split('=') for feat in word.feats.split('|'))
    else:
        return {}

def mkgender(ch):
    def gender(word):
        if word.text in ('Хілларі',):
            return 'Fem'

        if word.text in ('Бернар', 'Андраніка',):
            return 'Masc'

        # really???
        if word.lemma == 'вона':
            return 'Fem'

        if word.feats:
            return featdict(word).get('Gender') or featdict(ch[word].get('nsubj')).get('Gender')
    return gender

def animate(word):
    if word.feats:
        return featdict(word).get('Animacy') == 'Anim'

# prove by showing absent conjuncts?
def singular(word):
    if word.feats:
        return featdict(word).get('Number') == 'Sing'

def perspron(word):
    if word.feats:
        return featdict(word).get('PronType') == 'Prs' and word.upos == 'PRON'

def case(word):
    if word.feats:
        return featdict(word).get('Case')

def mkvocabulary(path='/home/liudmyla/fem_voc.txt'):
    with open(path) as f:
        for line in f:
            if ' – ' in line:
                l, r = line.strip().split(" – ")
                yield (l.lower(), [x.strip().lower() for x in filter(None, r.split(','))])

jobtitles = dict(mkvocabulary())
jobtitles['лінгвіст'] = ['лінгвіст']

def children(sent):
    z = defaultdict(dict)

    for f,r,t in sent.dependencies:
        if r == 'root':
            f = 'root'
        z[f][r] = t

    return z

def exempt(word):
    return word.lemma in ('голова',) # cf https://uk.wikipedia.org/wiki/%D0%A4%D0%B5%D0%BC%D1%96%D0%BD%D1%96%D1%82%D0%B8%D0%B2%D0%B8

def verify(sent):
    for proof,rel,offender in verify1(sent):
        if not exempt(offender):
            yield proof,rel,offender

def verify1(sent):
    ch = children(sent)
    gender1 = mkgender(ch)
    gender = {w: gender1(w) for w in sent.words}

    for _ in range(2):
        for f,r,t in sent.dependencies:
            if singular(f) and not gender[f] == 'Fem' and f.upos == 'NOUN' and animate(f) and \
                    r == 'flat:title' and \
                    gender[t] == 'Fem' and animate(t):
                gender[f] = 'Fem'
                if f.deprel == 'nsubj':
                    # propagate upwards to handle verbs like
                    # "3:бути(s,VERB,Aspect=Imp|Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin)"
                    gender[sent.words[f.head-1]] = 'Fem'
                yield t,r,f

            if f.upos == 'VERB' and gender[f] == 'Fem' and \
                    r == 'nsubj' and \
                    t.upos == 'NOUN' and not gender[t] == 'Fem':
                gender[t] = 'Fem'
                yield f,r,t

            # йде з посади заступника
            if f.upos == 'VERB' and gender[f] == 'Fem' and \
                    r == 'obl':
                nmod = ch[t].get('nmod')
                if nmod and gender[nmod] != 'Fem' and nmod.lemma in jobtitles:
                    gender[nmod] = 'Fem'
                    yield f,f'obl-nmod-jobtitle',nmod

            # почала працювати
            if f.upos == 'VERB' and gender[f] == 'Fem' and \
                    r == 'xcomp' and \
                    t.upos == 'VERB' and not gender[t] == 'Fem':
                gender[t] = 'Fem'
                yield f,r,t

            # Я проходила комісію щороку, я ж військовий льотчик
            if f.upos == 'VERB' and gender[f] == 'Fem' and \
                    r == 'parataxis' and \
                    t.upos == 'NOUN' and not gender[t] == 'Fem':
                gender[t] = 'Fem'
                yield f,r,t

            # А цього року Юристом року 2010 мене визнала Юридична практика
            # Радянська Україна незабаром стала європейським лідером
            if f.upos == 'VERB' and \
                    r == 'xcomp:sp' and \
                    not gender[t] == 'Fem': # and t.lemma in jobtitles:

                # look for extra proof:
                nsubj = ch[f].get('nsubj')
                obj = ch[f].get('obj')

                if nsubj is not None and (animate(nsubj) or perspron(nsubj)) and gender[nsubj] == 'Fem':
                    # Першим !тренером ~була Раїса Безсонова
                    gender[t] = 'Fem'
                    yield f,r,t
                elif obj is not None and (animate(obj) or perspron(obj)) and gender[obj] == 'Fem':
                    # Партія висунула(f) Юлію(obj) Тимошенко кандидатом(t) на присудження Нобелівської премії миру
                    # ЦВК визнала(f) її(obj) обраним президентом(t) України
                    gender[t] = 'Fem'
                    yield f,r,t
                elif nsubj is None and obj is None and t.lemma in jobtitles:
                    # Згодом стала активним членом Спілки театральних діячів
                    gender[t] = 'Fem'
                    yield f,r,t

            # Вона у нас як той дракон що дихає вогнем і відлякує ворогів
            # Після семи турів у неї 4 очки і перед шостим туром вона була лідером цих змагань
            #if f.upos == 'NOUN' and not gender(f) == 'Fem' and not case(f) == 'Acc' and \
            if f.upos == 'NOUN' and not gender[f] == 'Fem' and \
                    r == 'nsubj' and \
                    (animate(t) or perspron(t)) and gender[t] == 'Fem':
                gender[f] = 'Fem'
                yield t,r,f

            # Юна дизайнер
            if singular(f) and not gender[f] == 'Fem' and f.lemma in jobtitles and \
                    r == 'amod' and \
                    gender[t] == 'Fem' and \
                    True: #case(f) == case(t):
                gender[f] = 'Fem'
                yield t,r,f

            # Юний дизайнерка
            if singular(f) and gender[f] == 'Fem' and \
                    r == 'amod' and \
                    not gender[t] == 'Fem':
                gender[t] = 'Fem'
                yield f,r,t


def fmt(word, feats=False):
    gender = mkgender({word: {}})
    g = (gender(word) or '')[:1].lower()
    a = 'a' if animate(word) else ''
    j = 'j' if word.lemma in jobtitles else ''
    s = 's' if singular(word) else ''
    c = case(word)
    c = f',{c}' if c else ''
    feats = f',{word.feats}' if feats else ''

    return f'{word.id}:{word.text}({g}{a}{j}{s}{c},{word.upos}{feats})'

if __name__ == '__main__':
    nlp = stanza.Pipeline(lang='uk')

    for line in sys.stdin:
        n, text = line.strip().split(':')
        s = nlp(text).sentences[0]

        deps = list(verify(s))
        if deps:
            print(n, text, sep=':')
