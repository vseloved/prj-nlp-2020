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

## 3. Added more features
```
              precision    recall  f1-score   support

       False       0.98      1.00      0.99     51560
        True       0.57      0.11      0.19       910

    accuracy                           0.98     52470
   macro avg       0.78      0.56      0.59     52470
weighted avg       0.98      0.98      0.98     52470
```

## 4. Added more data
```
              precision    recall  f1-score   support

       False       0.98      1.00      0.99    839744
        True       0.63      0.15      0.24     15608

    accuracy                           0.98    855352
   macro avg       0.81      0.58      0.62    855352
weighted avg       0.98      0.98      0.98    855352
```

## 5. Trained the model on MASC corpus, and ran the evaluation on test data provided in run-on-test.json

```
              precision    recall  f1-score   support

       False       0.98      1.00      0.99      4166
        True       0.82      0.32      0.46       146

    accuracy                           0.97      4312
   macro avg       0.90      0.66      0.73      4312
weighted avg       0.97      0.97      0.97      4312
```