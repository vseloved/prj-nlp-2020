import sys
import re

from google_ngram_downloader import readline_google_store


if __name__ == "__main__":
    n = sys.argv[1]
    position = sys.argv[2]
    with open(f'{position}-{n}-grams.txt','w') as f: 
        for fname, url, records in readline_google_store(ngram_len=int(n)): 
            if re.search(r'[b-z][a-z]\.gz$', fname):
                print(fname)
                counter = 0
                for r in records:
                    if counter % 1000000 == 0:
                        print(r.ngram)
                    if position == 'tailing':
                        if re.search(r'^[a-zA-Z]', r.ngram) and r.ngram.endswith("._. _END_"): 
                            f.write('{}\n'.format(r.ngram))
                    if position == "inner":
                        if all([
                            " ._. " in r.ngram,
                            " ._. ]" not in r.ngram,
                            " ._. /" not in r.ngram,
                            " ._. *" not in r.ngram,
                            not r.ngram.startswith("._."),
                            not r.ngram.endswith("_END_"),
                            not r.ngram.endswith("_."),
                        ]):
                            f.write('{}\n'.format(r.ngram))
                    counter += 1
                            