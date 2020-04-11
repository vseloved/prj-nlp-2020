from os import walk
import json
import re
from langdetect import detect
from langid.langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

DATA_PATH = "../data/raw_data/"
PROCESSED_DATA_PATH = "../data/processed_data/"


def comments_from_file(file):
    comments = []
    file_name = DATA_PATH + file
    with open(file_name) as json_file:
        data = json.load(json_file)
        comments_section = data["data"]["comments"]
        for comment in comments_section:
            comments.append([comment["mark"], clean_html(comment["text"])])
    return comments


def clean_html(text):
    clean_tags = re.compile('<.*?>')
    iteration = re.sub(clean_tags, '', text)
    clean_new_lines = re.compile('\n')
    return re.sub(clean_new_lines, '', iteration)


def is_valid_comment(comment):

    if comment[0] is None:
        return False

    if comment[0] == 0:
        return False

    if comment[1] == '':
        return False

    language = ''
    try:
        # language = detect(comment[1])
        language = identifier.classify(comment[1])[0]
    except:
        pass

    return comment[0] is not None and \
           comment[0] > 0 \
           and comment[1] != '' \
           and language == 'uk'


if __name__ == '__main__':

    json_files = []
    for (dirpath, dirnames, filenames) in walk(DATA_PATH):
        json_files.extend(filenames)
        break

    inbound_comments = []
    for file in json_files:
        loaded_comments = comments_from_file(file)
        inbound_comments.extend(loaded_comments)

    print("Unfiltered comments: ", len(inbound_comments))

    outbound_comments = []
    counter = 0
    for comment in inbound_comments:
        counter += 1
        # print (counter)
        if counter % 100 == 0:
            print('processed', counter, 'comments', 'filtered',len(outbound_comments))

        if is_valid_comment(comment):
            outbound_comments.append(comment)

    with open(PROCESSED_DATA_PATH + '02-extracted-comments.json', 'w', encoding='utf-8') as f:
        json.dump(outbound_comments, f, ensure_ascii=False, indent=4)

    print("Filtered comments: ", len(outbound_comments))
