import re
import csv
import wikipedia as w
import spacy

nlp = spacy.load("en_core_web_md")

band_name = "Drudkh"

page = w.page(band_name)
chunks = page.content.split("\n")

potential_album_chunks = [c for c in chunks if re.search(r'\b(EP|album|single)\b', c, flags=re.I)]

ALBUM_REGEX = r'{}\b[^.]+?\b(EP|album|single)\b[^.]+?\bby\b[^.]+?\b{}\b[^.]+?(\breleased\b)?[^.]+?\b(?P<year>[0-9][0-9][0-9][0-9])\b.+?'
LABEL_REGEX = r'(\blabel {}\b|\b{} label\b)'

# print(potential_album_chunks)
potential_labels = set()
albums = {}
all_entities = set()
for chunk in potential_album_chunks:
    doc = nlp(chunk)
    for sent in doc.sents:
        for ent in sent.ents:
            if not re.search(r'[а-яА-Я]+', ent.text) and ent.text.count("(") == ent.text.count(")"):
                all_entities.add(ent.text)

for entity in all_entities:
    potential_album = entity
    try:
        p = w.page(entity)
    except w.exceptions.DisambiguationError:
        entities = w.search(entity)
        filtered_entities = list(filter(lambda x: re.search(r'\(({}\s|\s)?(EP|album|single)\)'.format(band_name), x, flags=re.I), entities))
        if not filtered_entities:
            continue
        entity = filtered_entities[0]
    except w.exceptions.PageError:
        continue
    try:
        potential_album_page = w.page(entity)
    except w.exceptions.DisambiguationError:
        # you are here 'cause you are using libs from pypi instead your own solutions! :\
        continue
    if band_name not in potential_album_page.content:
        continue
    album_search = re.search(ALBUM_REGEX.format(potential_album, band_name), potential_album_page.content, flags=re.I)
    if album_search:
        albums[entity] = {"year":album_search.groupdict().get('year'), "content":potential_album_page.content}
        for e in all_entities:
            if re.search(LABEL_REGEX.format(e, e), potential_album_page.content, flags=re.I):
                potential_labels.add(e)
print(potential_labels)
filtered_labels = [l for l in potential_labels if not [i for i in potential_labels if l in i and l != i]]

with open("albums_wikipedia.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["album", "year", "label"])
    for album, info in albums.items():
        for label in filtered_labels:
            if label in info["content"]:
                info["label"] = label
                break
        print(f'Album: {album}, Year: {info.get("year","")}, Label: {info.get("label","")}')
        writer.writerow([album, info.get("year", ""), info.get("label", "")])
