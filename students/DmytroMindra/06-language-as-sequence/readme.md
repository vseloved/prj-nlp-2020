# Language as sequence

## 1. Data

I am using "MASC WORD SENSE SENTENCE CORPUS, TSV VERSION 1.0"
Downloaded it from this URL: http://www.anc.org/data/masc/downloads/data-download/

```
data/raw-data/masc_sentences.tsv
```

## 2. Baseline
Logistic regression on (token + lemma + pos + deprel)
```
              precision    recall  f1-score   support

       False       0.98      1.00      0.99    119797
        True       0.51      0.01      0.02      2188

    accuracy                           0.98    121985
   macro avg       0.75      0.51      0.51    121985
weighted avg       0.97      0.98      0.97    121985
```
