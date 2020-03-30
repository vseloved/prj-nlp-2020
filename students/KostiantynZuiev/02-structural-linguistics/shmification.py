from nltk.tokenize import word_tokenize
import re
import string
import sys

vowels = ("A", "E", "I", "O", "U",)
consonants = ("B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "X", "Y", "Z")

def shmificate_text(text):
    tokens = word_tokenize(text)
    if len(tokens) == 1:
        token = tokens[0]
        shmificated = shmificate_token(token)
        result = f'{text}-{shmificated}'

        return result
    elif len(tokens) == 2:
        if any([p for p in string.punctuation if p in tokens[1]]):
            token = tokens[0]
            shmificated = shmificate_token(token)
            result = f'{text}-{shmificated+tokens[1]}'

            return result
        else:
            token = tokens[1]
            shmificated = shmificate_token(token)
            result = f'{text}-{tokens[0]} {shmificated}'

            return result
    elif len(tokens) > 2:
        token = tokens[-1]
        shmificated = shmificate_token(token)
        if token == shmificated:

            return f'Not shmificated ): {text}-{text}'
        result_string = ""
        for token in tokens[:-1]:
            if any([p for p in string.punctuation if p in token]):
                result_string = result_string.strip() + token
            else:
                result_string += f' {token}'
        result = f'{text}-{result_string.strip()} {shmificated}'

        return result

def shmificate_token(token):
    shmificated=token
    is_upper = token.isupper()
    shmefix = 'sm' if "sh" in token.lower() else "shm"
    shmefix = shmefix if token[0].islower() else shmefix.capitalize()
    if is_upper:
        shmefix = shmefix.upper()
    if any([token.lower().startswith(v.lower()) for v in vowels]):
        token = token if is_upper else token.lower()
        shmificated = shmefix + token
    if any([token.lower().startswith(c.lower()) for c in consonants]):
        if token.lower().startswith("shm") or token.lower().startswith("schm"):
            shmificated = token
        else:
            # TODO: probably it's better to use regex to find opening subsequence that ends with 'H'
            shmificated = shmefix + token[1:] if token[1].lower() != 'h' else shmefix + token[2:]

    return shmificated

if __name__ == "__main__":
    text = sys.argv[1]
    r = shmificate_text(text)
    print(r)