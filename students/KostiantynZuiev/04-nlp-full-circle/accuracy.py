import csv

db_albums = []
with open('albums_dbpedia.csv', 'r') as db_f:
    reader = csv.DictReader(db_f)
    for row in reader:
        db_albums.append({'album':row['album'], 'year': row['year'], 'label': row['label']})

wiki_albums = []
with open('albums_wikipedia.csv', 'r') as db_wiki:
    reader = csv.DictReader(db_wiki)
    for row in reader:
        wiki_albums.append({'album':row['album'], 'year': row['year'], 'label': row['label']})

max_count_accuracy = 0.3
max_album_accuracy = 0.4
max_year_accuracy = 0.1
max_genre_accuracy = 0.0
max_label_accuracy = 0.1

# count accuracy
count_accuracy = (len(wiki_albums) * max_count_accuracy)/len(db_albums)

# album accuracy
album_accuracy_points = 0
for w_a in wiki_albums:
    for d_a in db_albums:
        if w_a['album'] == d_a['album']:
            album_accuracy_points += 1
            break
        elif w_a['album'] in d_a['album']:
            album_accuracy_points += 0.7
            break
        elif d_a['album'] in w_a['album']:
            album_accuracy_points += 0.5
            break

album_accuracy = (album_accuracy_points * max_album_accuracy)/len(db_albums)

# year accuracy
year_accuracy_points = 0
for w_a in wiki_albums:
    for d_a in db_albums:
        if w_a['year'] == d_a['year']:
            year_accuracy_points += 1
            break

year_accuracy = (year_accuracy_points * max_year_accuracy)/len(db_albums)

# genre accuracy

genre_accuracy = max_genre_accuracy

# label accuracy
label_accuracy_points = 0
for w_a in wiki_albums:
    for d_a in db_albums:
        if w_a['label'] == d_a['label']:
            label_accuracy_points += 1
        elif w_a['label'] == 'Underground Activists' and \
                d_a['label'] == 'Season of Mist':
            label_accuracy_points += 0.3

label_accuracy = (label_accuracy_points * max_label_accuracy)/len(db_albums)

total_accuracy = count_accuracy + album_accuracy + year_accuracy + genre_accuracy + label_accuracy

print("Album count accuracy: ", count_accuracy)
print("Album name accuracy: ", album_accuracy)
print("Album year accuracy: ", year_accuracy)
print("Album genre accuracy: ", genre_accuracy)
print("Album label accuracy: ", label_accuracy)
print("Total accuracy: ", total_accuracy)