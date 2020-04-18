import json
import re
from langid.langid import LanguageIdentifier, model

identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
from pathlib import Path
from tqdm import tqdm

data_path = './data'
cleaned_data_path = './cleaned_data'
data_files = list(Path(data_path).glob("*.json"))

loaded_comments = []
validated_comments = []
out_comments = []

clean_tags = re.compile('<.*?>')
clean_new_lines = re.compile('\n')
clean_hash_tags = re.compile('#(\S*)')


def extract_comments(file):
    comments = []
    with open(file) as json_file:
        data = json.load(json_file)
        comments_pull = data["data"]["comments"]
        for comment in comments_pull:
            comments.append([comment["mark"], clean_from_html(comment["text"]),''])
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

def write_to_file_data_set(comments, lang):
    comments_lang = list(filter(lambda comment: comment[2] == lang, comments))

    dev_size = round(len(comments_lang) * 0.7)

    dev_set = comments_lang[:dev_size]
    test_set = comments_lang[dev_size:]

    with open(cleaned_data_path + '/' + lang + '/'+ 'dev_set.json', 'w', encoding='utf-8') as f:
        json.dump(dev_set, f, ensure_ascii=False, indent=2)

    with open(cleaned_data_path + '/' + lang + '/' + 'test_set.json', 'w', encoding='utf-8') as f:
        json.dump(test_set, f, ensure_ascii=False, indent=2)
    return len(comments_lang)


for file in tqdm(data_files):

    loaded_comments = extract_comments(file)
    validated_comments = validate(loaded_comments)
    if len(validated_comments) > 0:
        out_comments.extend(validated_comments)

for lang in ['uk','ru']:
    print(write_to_file_data_set(out_comments,lang))

