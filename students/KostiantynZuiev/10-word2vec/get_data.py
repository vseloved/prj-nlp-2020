import gzip
import json
import os
import langid

DATA_PATH = '/home/holdbar/projects/1551.gov.ua/raw/'

TOP_CATEGORIES_COUNTS = [
    ('Відсутність ГВП', 13273),
    ('Укладання та ремонт асфальтного покриття', 6632),
    ('Відсутність опалення', 6020),
    ('Перевірка дозвільної документації, демонтаж кіосків, ларків', 3654),
    ('Прибирання та санітарний стан територій', 3084),
    ('Не працює пасажирський ліфт', 2718),
    ('Відсутність освітлення у під\'їзді за відсутності/несправності лампочок', 2637),
    ('Відновлення благоустрою після вик. планових,аварійних робіт на об\'єктах благоуст', 2393),
    ('Незадовільна температура ГВП', 2304),
    ('Технічний стан проїжджих частин вулиць та тротуарів', 2180)
]

TOP_CATEGORIES = [t[0] for t in TOP_CATEGORIES_COUNTS]

def read_file(file_path):
    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        info = json.load(f)

        return info[0]["CallZType"], info[0]["CallZText"]

dataset = []
    
for subdir in os.listdir(DATA_PATH):
    subdir_path = f'{DATA_PATH}{subdir}/'
    for file_name in os.listdir(subdir_path):
        file_path = f'{subdir_path}{file_name}'
        label, text = read_file(file_path)
        if langid.classify(text)[0] == "uk":
            dataset.append([label, text])

with open('dataset.json','w') as w:
    json.dump(dataset, w)
