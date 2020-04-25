import json

PROCESSED_DATA_FILE = "../data/processed_data/02-extracted-comments.json"
DATASETS_PATH = "../data/datasets/"

if __name__ == '__main__':

    print ("On this step we split the data into training and evaluation datasets." )

    with open(PROCESSED_DATA_FILE) as json_file:
        data = json.load(json_file)


    data_entities = len(data)

    training_set_size = round(len(data)*0.7)
    eval_set_size = data_entities - training_set_size

    training_set = data[:training_set_size]
    eval_set = data[training_set_size:]

    print('total comments:', data_entities)
    print('training set', len(training_set))
    print('eval set', len(eval_set))

    with open(DATASETS_PATH + 'training_set.json', 'w', encoding='utf-8') as f:
        json.dump(training_set, f, ensure_ascii=False, indent=4)

    with open(DATASETS_PATH + 'eval_set.json', 'w', encoding='utf-8') as f:
        json.dump(eval_set, f, ensure_ascii=False, indent=4)