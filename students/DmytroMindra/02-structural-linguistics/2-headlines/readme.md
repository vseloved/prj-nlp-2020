# Homework 2 
 
## 2-1: The Associated Press Stylebook Headline Formatting 
 
Getting the dependencies:
```
pip install -r requirements.txt
```

Getting help:
```
python -m headlines --help
Usage: __main__.py [OPTIONS]

Options:
  --cat / --no-cat
  --evalset
  --corpus
  --virality
  --help
```

#### Running an evaluation on a test set
```
python -m headlines --evalset
```
Results: [evalset-output.txt](evalset-output.txt)

```
Passed : 95
Failed : 5
total : 100
Total score on evalset 95/100 = 0.950%
```

#### Running an evaluation on examiner-headlines corpus
```
python -m headlines --corpus
```
Results:

```
Passed : 643
Failed : 4357
total : 5000
Total score on examiner-headlines corpus 643/5000 = 0.129%
```

## 2-2: Headline Virality

```
python -m headlines --virality
```

Results:
```
Contains named entity (person/organisation): 53.04%
Has positive scent: 40.46%
Has negative scent: 25.56%
Contains comparative or superlative: 4.70%
Total headlines: 5000.00
```