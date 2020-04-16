### Дані

1. Тренувальні дані були згенеровані з [корпусу OANC](http://www.anc.org/data/oanc/download/)
2. н-грами брались з [phrasefinder](https://phrasefinder.io). Я качала триграми (для тестувальних і тренувальних токенів), хоча, по суті, користувалась тільки наступним словом. Спойлер: використання н-грамів чомусь не покращило результат :(

### Бейзлайн і покращення

1. Проста фіча - текст слова

```
             precision recall f1-score
False             0.96    1.0     0.98
True              0.75   0.05      0.1

accuracy                          0.96
macro avg         0.85   0.53     0.54
weighted avg      0.95   0.96     0.94
```

2. Сусідні (по два вправо і вліво) слова

```
             precision recall f1-score
False             0.98    1.0     0.99
True              0.88   0.62     0.73

accuracy                          0.98
macro avg         0.93   0.81     0.86
weighted avg      0.98   0.98     0.98
```

3. Частина мови

```
             precision recall f1-score
False             0.98    1.0     0.99
True              0.88   0.62     0.73

accuracy                          0.98
macro avg         0.93   0.81     0.86
weighted avg      0.98   0.98     0.98
```

4. Частини мови сусідніх (по два вправо і вліво) слів

```
             precision recall f1-score
False             0.98    1.0     0.99
True              0.88   0.62     0.73

accuracy                          0.98
macro avg         0.93   0.81     0.86
weighted avg      0.98   0.98     0.98
```

5. Форма слова (+ форми слова сусідніх слів)

```
             precision recall f1-score
False             0.99    1.0     0.99
True              0.87   0.71     0.78

accuracy                          0.98
macro avg         0.93   0.85     0.89
weighted avg      0.98   0.98     0.98
```

6. н-грами (частота вживання слів поруч + наступна частина мови) -

```
             precision recall f1-score
False             0.99    1.0     0.99
True              0.87   0.71     0.78

accuracy                          0.98
macro avg         0.93   0.85     0.89
weighted avg      0.98   0.98     0.98

```

7. результат на тестовій вибірці

```
              precision    recall  f1-score   support

       False       0.97      0.99      0.98      4542
        True       0.37      0.26      0.30       155

    accuracy                           0.96      4697
   macro avg       0.67      0.62      0.64      4697
weighted avg       0.95      0.96      0.96      4697
```

### Загальні висновки

Вцілому результати мені видаються трохи дивними, тому підозрюю, що або я взагалі все робила невірно, або припустилась десь помилки `¯\_(ツ)_/¯`
