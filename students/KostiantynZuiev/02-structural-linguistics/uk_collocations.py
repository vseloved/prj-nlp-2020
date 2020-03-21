import pymorphy2

from nltk.tokenize import word_tokenize

morph = pymorphy2.MorphAnalyzer(lang="uk")

if __name__ == "__main__":
    with open('data/tyhrolovy.txt','r') as f:
        result_dict = {}
        for line in f:
            tokens = word_tokenize(line)
            for i,token in enumerate(tokens):
                possible_adj = morph.parse(token)
                if "ADJF" in possible_adj[0].tag:
                    
                    try:
                        possible_noun = morph.parse(tokens[i+1])
                        if "NOUN" in possible_noun[0].tag and "anim" in possible_noun[0].tag:
                            phrase = f'{token} {tokens[i+1]}'.lower()
                            if result_dict.get(phrase) is None:
                                result_dict[phrase] = 1
                            else:
                                result_dict[phrase] += 1
                    except IndexError:
                        continue
        
        with open('uk_collocations_results.txt', 'w') as res_file:
            for phrase, count in result_dict.items():
                res_file.write(f'{count}: {phrase}\n')

