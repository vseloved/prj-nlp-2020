import spacy

nlp = spacy.load('/tmp/uk_vectors')

def vec(text):
    return nlp(text)[0].vector

def vectorize(tokens):
    v = vec('unk')
    
    for t in tokens:        
        v += vec(t)
            
    v /= len(tokens)

    return v