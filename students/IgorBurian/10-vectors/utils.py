import json
import gzip
import glob
import pandas as pd
from tqdm import tqdm
import pickle
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


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

def load_data(name):
    with open('{}.pickle'.format(name), 'rb') as f:
        return pickle.load(f)

# TODO: add timestamp
def log_result(experiment, result):
    with open('experiments.json', mode='a+', encoding='utf-8') as out:
        out.write(json.dumps({ 'name': experiment, 'stats': result.to_json() }))

def run_experiment(name, model, x, y):  
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    result = pd.DataFrame(classification_report(y_test, y_pred, output_dict=True))
    log_result(name, result)
    
    return result

def dump_data(name, data):
    with open('{}.pickle'.format(name), 'wb') as f:  
        pickle.dump(data, f)