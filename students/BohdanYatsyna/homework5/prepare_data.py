import json
import re
from langid.langid import LanguageIdentifier, model

identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
from pathlib import Path
from tqdm import tqdm
import stanza

data_path = './data'
cleaned_data_path = './cleaned_data'
data_files = list(Path(data_path).glob("*.json"))

loaded_comments = []
validated_comments = []
out_comments = []
out_comments_tok = []
out_comments_lem = []

clean_tags = re.compile('<.*?>')
clean_new_lines = re.compile('\n')
clean_hash_tags = re.compile('#(\S*)')

nlp = stanza.Pipeline(lang='uk', processors='tokenize,mwt,pos,lemma')


def extract_comments(file):
    comments = []
    with open(file) as json_file:
        data = json.load(json_file)
        comments_pull = data["data"]["comments"]
        for comment in comments_pull:
            comments.append([comment["mark"], clean_from_html(comment["text"]), ''])
    return comments


def clean_from_html(text):
    clean_text = ''
    iteration = re.sub(clean_tags, '', text)
    iteration = re.sub(clean_new_lines, '', iteration)
    iteration = re.sub(clean_hash_tags, '', iteration)
    return iteration


def validate(comments):
    valid_comments = []
    for cmt in comments:
        # перевірка чи є данні в коменті
        if cmt[0] in [None, 0]:
            continue
        if cmt[1] == '':
            continue
        # перевірка мови
        try:
            language = identifier.classify(cmt[1])[0]
            if language == 'uk':
                cmt[2] = 'uk'
            if language == 'ru':
                cmt[2] = 'ru'
        except:
            pass
        valid_comments.append(cmt)
    return valid_comments


def write_to_file_data_set(comments, tok_comments, lem_comments, lang):
    comments_lang = list(filter(lambda comment: comment[2] == lang, comments))
    tok_comments_lang = list(filter(lambda tok_comments: tok_comments[2] == lang, tok_comments))
    lem_comments_lang = list(filter(lambda lem_comments: lem_comments[2] == lang, lem_comments))

    ### Звичайний датасет
    dev_size = round(len(comments_lang) * 0.7)
    dev_set = comments_lang[:dev_size]
    test_set = comments_lang[dev_size:]
    # просто складені коменти
    with open(cleaned_data_path + '/' + lang + '/' + 'dev_set.json', 'w', encoding='utf-8') as f:
        json.dump(dev_set, f, ensure_ascii=False, indent=2)

    with open(cleaned_data_path + '/' + lang + '/' + 'test_set.json', 'w', encoding='utf-8') as f:
        json.dump(test_set, f, ensure_ascii=False, indent=2)
    # Токенізованний датасет
    dev_size = round(len(tok_comments_lang) * 0.7)
    dev_set = tok_comments_lang[:dev_size]
    test_set = tok_comments_lang[dev_size:]
    with open(cleaned_data_path + '/' + lang + '/' + 'tok_dev_set.json', 'w', encoding='utf-8') as f:
        json.dump(dev_set, f, ensure_ascii=False, indent=2)

    with open(cleaned_data_path + '/' + lang + '/' + 'tok_test_set.json', 'w', encoding='utf-8') as f:
        json.dump(test_set, f, ensure_ascii=False, indent=2)

    # Лемматизованний датасет
    dev_size = round(len(lem_comments_lang) * 0.7)
    dev_set = lem_comments_lang[:dev_size]
    test_set = lem_comments_lang[dev_size:]
    with open(cleaned_data_path + '/' + lang + '/' + 'lem_dev_set.json', 'w', encoding='utf-8') as f:
        json.dump(dev_set, f, ensure_ascii=False, indent=2)

    with open(cleaned_data_path + '/' + lang + '/' + 'lem_test_set.json', 'w', encoding='utf-8') as f:
        json.dump(test_set, f, ensure_ascii=False, indent=2)
    return len(comments_lang), len(tok_comments_lang), len(lem_comments_lang)


# токенізатор тексту
def words_tokenize(message):
    doc = nlp(message)
    tokens = []
    for sentence in doc.sentences:
        for token in sentence.tokens:
            tokens.append(token.text)
    return tokens


# тут перетворюеємо меседж на токени з різними удосконаленнями
def process_message(message, lower_case=True):
    if lower_case: message = message.lower()
    words = words_tokenize(message)
    return words


def tokenize_lemmatize_comments(comments):
    tokenized_comments = []
    lemmatized_comments = []

    for cmt in comments:
        tok_cmt = ""
        lem_cmt = ""
        doc = nlp(cmt[1])
        for sent in doc.sentences:
            for word in sent.words:
                if len(tok_cmt) == 0:
                    tok_cmt = word.text
                    lem_cmt = word.lemma
                else:
                    tok_cmt = tok_cmt + ' ' + word.text
                    lem_cmt = lem_cmt + ' ' + word.lemma
        tokenized_comments.append([cmt[0], tok_cmt,cmt[2]])
        lemmatized_comments.append([cmt[0], lem_cmt,cmt[2]])
    return tokenized_comments, lemmatized_comments


for file in tqdm(data_files):

    loaded_comments = extract_comments(file)
    validated_comments = validate(loaded_comments)
    if len(validated_comments) > 0:
        tokenized_comments, lemmatized_comments = tokenize_lemmatize_comments(validated_comments)
        out_comments.extend(validated_comments)
        out_comments_tok.extend(tokenized_comments)
        out_comments_lem.extend(lemmatized_comments)

for lang in ['uk']:
    print(write_to_file_data_set(out_comments, out_comments_tok, out_comments_lem, lang))
