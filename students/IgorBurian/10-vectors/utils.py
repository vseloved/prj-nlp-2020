import json
import gzip
import glob
import pandas as pd
from tqdm import tqdm
import pickle


def read_file(path):
    with gzip.open(path, 'rb') as f:
        req = json.load(f)
        return req[0]['CallZText'], req[0]['CallZType']

def load_1551():
    PATH = '1551.gov.ua/raw/'
    data = []
        
    files = glob.glob(PATH + '*/*')
    
    for path in tqdm(files, total=len(files)):
        data.append(read_file(path))
    
    df = pd.DataFrame(data, columns=['text', 'category'])
    df = df[df.text != '']
        
    return df

def load_stopwords():
    result = []
    with open('stopwords.txt') as lines:
        for l in lines:
            result.append(l.strip())
    return result

def load_data():
    with open('data.pickle', 'rb') as f:
        return pickle.load(f)