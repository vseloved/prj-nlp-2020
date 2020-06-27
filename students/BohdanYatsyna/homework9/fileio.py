import json

def read_jsonnl(file):
    with open(file, "r") as f:
        data = [json.loads(line) for line in f.readlines()]
        return data
