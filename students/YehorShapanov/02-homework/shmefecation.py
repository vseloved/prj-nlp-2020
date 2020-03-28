def find_vowel(word):
    for i,c in enumerate(word):
        if c.lower() in "aeuio":
            return i
    return -1

def has_sh(w):
    return w[1:].find('sh') != -1

def perform_reduplication(s):
    tokens = s.split(" ")
    if len(tokens)==0: return ""
    target_word = tokens[-1].lower()

    if len(target_word)>2 and target_word[:3]=="sch":
        return s

    prefix = "shm"
    if has_sh(target_word):
        prefix = "sm"

    v_pos = find_vowel(target_word)
    target_word = prefix + target_word[v_pos:]

    if tokens[-1].isupper():
        target_word = target_word.upper()
    elif tokens[-1].istitle():
        target_word = target_word.title()

    tokens = tokens[:-1] + [target_word]
    return " ".join(tokens)

test_cases = ['schmuck', 'shmaltz', 'APPLE', 'data science', 'Ashmont', 'This is a sentence.']
for t in test_cases:
    print(perform_reduplication(t))