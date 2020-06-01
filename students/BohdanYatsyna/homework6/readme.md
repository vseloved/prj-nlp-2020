Послідовність запуску скриптів

взяв датасет  masc_sentences.tsv з https://www.anc.org/data/masc/wordnet-framenet-annotations/
1. спочатку запускаємо ```preproces.py```  - отримуєм очищений набір речень
2. потім ```preprocess1.py``` - що готує нам файл dataset. json у якому уже поклеєні речення та заекстрачені фічі з кожного токена у реченні. Розбитий вже на train та test
3. ```prediction.py```  - пропускає через пошук сіткою Gridsearch с параметрами (залишив лише ті що дають найкращий результат)
4. ```trainclf.py``` - тренує классифікатор щоб можна було подивитись на кращі фічі

перше наближення:

```json
pipeline: ['tfidf', 'clf']


{'tfidf__use_idf': (False,), 'tfidf__norm': ('l2',), 'clf__tol': (0.0001,), 'clf__solver': ('sag',), 'clf__penalty': ('l2',), 'clf__max_iter': (200,), 'clf__random_state': (12,)}


Best score: 0.991
	clf__max_iter: 200
	clf__penalty: 'l2'
	clf__random_state: 12
	clf__solver: 'sag'
	clf__tol: 0.0001
	tfidf__norm: 'l2'
	tfidf__use_idf: False


              precision    recall  f1-score   support

       False       0.99      1.00      1.00    798587
        True       0.89      0.15      0.26      8496

    accuracy                           0.99    807083
   macro avg       0.94      0.58      0.63    807083
weighted avg       0.99      0.99      0.99    807083

              precision    recall  f1-score   support

       False       0.97      1.00      0.98      4542
        True       0.56      0.03      0.06       155

    accuracy                           0.97      4697
   macro avg       0.76      0.52      0.52      4697
weighted avg       0.95      0.97      0.95      4697

Normalized confusion matrix
[[9.99119331e-01 8.80669309e-04]
 [9.67741935e-01 3.22580645e-02]]
```

найкращий результат:

```json

pipeline: ['tfidf', 'clf']


{'tfidf__use_idf': (False, True), 'tfidf__norm': ('l1', 'l2'), 'clf__tol': (0.0001, 1e-05), 'clf__solver': ('sag',), 'clf__penalty': ('l2',), 'clf__max_iter': (1000,), 'clf__random_state': (42,), 'clf__multi_class': ('multinomial',)}


Best score: 0.991
	clf__max_iter: 1000
	clf__multi_class: 'multinomial'
	clf__penalty: 'l2'
	clf__random_state: 42
	clf__solver: 'sag'
	clf__tol: 0.0001
	tfidf__norm: 'l2'
	tfidf__use_idf: True


              precision    recall  f1-score   support

       False       0.99      1.00      1.00    798488
        True       0.90      0.21      0.34      8546

    accuracy                           0.99    807034
   macro avg       0.94      0.60      0.67    807034
weighted avg       0.99      0.99      0.99    807034

              precision    recall  f1-score   support

       False       0.98      1.00      0.99      4542
        True       0.95      0.26      0.41       155

    accuracy                           0.98      4697
   macro avg       0.96      0.63      0.70      4697
weighted avg       0.97      0.98      0.97      4697

Normalized confusion matrix
[[9.99559665e-01 4.40334654e-04]
 [7.35483871e-01 2.64516129e-01]]
```

спостереження:

LogisticRegression  без multinomial значно погіршувало знаходження True
