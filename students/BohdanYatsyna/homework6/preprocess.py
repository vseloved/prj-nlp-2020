import csv
import json
from tqdm import tqdm
RAW_DATA_FILE = './masc/masc_sentences.tsv'
RAW_SENTENCES_FILE = '../stripped_masc_sentences.json'


def read_raw_data():
    data = []
    with open(RAW_DATA_FILE) as in_file:
        reader = csv.DictReader(in_file, dialect='excel-tab')
        for row in tqdm(reader):
            data.append(list(row.items())[6][1])

    with open(RAW_SENTENCES_FILE, 'w') as out_file:
        json.dump(data, out_file)


if __name__ == "__main__":
    read_raw_data()