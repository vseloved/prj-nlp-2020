# Homework 2-1: The Associated Press Stylebook Headline Formatting 
 

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
  --help 
```

You can find the output of current 

####Running an evaluation on a test set
```
python -m headlines --evalset
```
Results: [evalset-output.txt](evalset-output.txt)

####Running an evaluation on examiner-headlines corpus
```
python -m headlines --corpus
```
Results: [examiner-headlines-output.txt](examiner-headlines-output.txt)