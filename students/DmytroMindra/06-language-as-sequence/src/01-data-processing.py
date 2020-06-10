import csv
import json

RAW_DATA_FILENAME = '../data/raw-data/masc_sentences.tsv'
RAW_SENTENCES_FILENAME = '../data/raw-data/stripped_masc_sentences.json'


def read_raw_data():
    """
    Reading the original file
    Stripping it from the meta information and saving in json
    """
    data = []
    with open(RAW_DATA_FILENAME) as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in reader:
            data.append(list(row.items())[6][1])


    # processing all 500k sentences would be painful
    # so let's start from 1%
    with open(RAW_SENTENCES_FILENAME, 'w') as outfile:
        json.dump(data[:100000], outfile)


if __name__ == "__main__":
    read_raw_data()
