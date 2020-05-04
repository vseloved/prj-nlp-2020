### Висновки

0) В якості базового рішення я використав правило з частинами мови щоб визначити кінець\початок речення.
1) Датасет - важливий. Я спробував попрацювати з трьома датасетами: brown, gutenberg з nltk та дамп wikipedia 
за 2010 рік(його довелося обмежувати - забагато даних). Браун показав найкращий результат, гутенберг гірший, вікіпедія герший за гутенберг.
2) З фіч я поступово додавав: власне саме слово, сусідні слова, регістр слова й сусідів, лема слова й сусідів, частина мови слова й сусідів, н-грами.
3) Лема не дала покращення у всіх випадках, а в брауні не дали покращення й частини мови.
4) Н-грами не дали покращення на всіх датасетах. З н-грамами вийшло складно. Я не впевнений, що корректно їх використав. Я продивився COCA н-грами і не знайшов достатньо зустрічань кінця речення, тому я вирішив використати гуглові н-грами. З ними вийшла інша історія - їх дууууже багато. Я спробував зібрати н-грами кінців речень, щоб мати перелік з двох останніх слів які закінчують речення. Якщо я правильно зрозумів інструкцію то варто було шукати пари "останнєслово речення - перше слово наступного" але через дуже великий об'єм даних мені не вдалося зібрати хоч якусь кількість таких кейсів з гуглових н-грам. Окрім того я просто вважав, що якщо пара токенів є в переліку пар які я зібрав, то це і є фіча. При цьому за інструкцією(як я зрозумів) варто порівнювати частоту коли н-грама є кінцем речення і коли ні, але через величезний об'єм даних мені це видалося нераціональним. Тож я допускаю що через мій підхід до збору даних, їх невелику кількіст а також неправильно виділення цієї фічі я не отримав покращення за рахунок н-грам.

#### Baseline

TEST DATASET:
              precision    recall  f1-score   support

       False       0.97      1.00      0.99      4542
        True       0.90      0.24      0.38       155

    accuracy                           0.97      4697
   macro avg       0.94      0.62      0.68      4697
weighted avg       0.97      0.97      0.97      4697


#### Gutenberg

single word:
              precision    recall  f1-score   support

       False       0.96      1.00      0.98    239542
        True       0.46      0.01      0.02      9796

    accuracy                           0.96    249338
   macro avg       0.71      0.50      0.50    249338
weighted avg       0.94      0.96      0.94    249338

+neighbors:
              precision    recall  f1-score   support

       False       0.98      0.99      0.98    239542
        True       0.66      0.50      0.57      9796

    accuracy                           0.97    249338
   macro avg       0.82      0.74      0.78    249338
weighted avg       0.97      0.97      0.97    249338

+case:
              precision    recall  f1-score   support

       False       0.98      0.99      0.99    239542
        True       0.66      0.63      0.64      9796

    accuracy                           0.97    249338
   macro avg       0.82      0.81      0.81    249338
weighted avg       0.97      0.97      0.97    249338

+lemma:
              precision    recall  f1-score   support

       False       0.98      0.99      0.99    239542
        True       0.65      0.63      0.64      9796

    accuracy                           0.97    249338
   macro avg       0.82      0.81      0.81    249338
weighted avg       0.97      0.97      0.97    249338

+POS:
              precision    recall  f1-score   support

       False       0.99      0.99      0.99    239542
        True       0.69      0.69      0.69      9796

    accuracy                           0.98    249338
   macro avg       0.84      0.84      0.84    249338
weighted avg       0.98      0.98      0.98    249338

+N-gram:
              precision    recall  f1-score   support

       False       0.99      0.99      0.99    239542
        True       0.69      0.69      0.69      9796

    accuracy                           0.98    249338
   macro avg       0.84      0.84      0.84    249338
weighted avg       0.98      0.98      0.98    249338


TEST DATASET:
              precision    recall  f1-score   support

       False       0.98      0.99      0.98      4542
        True       0.51      0.45      0.48       155

    accuracy                           0.97      4697
   macro avg       0.75      0.72      0.73      4697
weighted avg       0.97      0.97      0.97      4697

#### WikiPedia

single word:
              precision    recall  f1-score   support

       False       0.98      1.00      0.99    101083
        True       0.77      0.01      0.01      2604

    accuracy                           0.98    103687
   macro avg       0.87      0.50      0.50    103687
weighted avg       0.97      0.98      0.96    103687

+neighbors:
              precision    recall  f1-score   support

       False       0.99      1.00      0.99    101083
        True       0.94      0.55      0.70      2604

    accuracy                           0.99    103687
   macro avg       0.97      0.78      0.85    103687
weighted avg       0.99      0.99      0.99    103687

+case:
              precision    recall  f1-score   support

       False       0.99      1.00      0.99    101083
        True       0.94      0.61      0.74      2604

    accuracy                           0.99    103687
   macro avg       0.96      0.80      0.87    103687
weighted avg       0.99      0.99      0.99    103687

+lemma:
              precision    recall  f1-score   support

       False       0.99      1.00      0.99    101083
        True       0.92      0.61      0.74      2604

    accuracy                           0.99    103687
   macro avg       0.95      0.81      0.86    103687
weighted avg       0.99      0.99      0.99    103687

+POS:
              precision    recall  f1-score   support

       False       0.99      1.00      1.00    101083
        True       0.91      0.68      0.78      2604

    accuracy                           0.99    103687
   macro avg       0.95      0.84      0.89    103687
weighted avg       0.99      0.99      0.99    103687

+N-gram:
              precision    recall  f1-score   support

       False       0.99      1.00      1.00    101083
        True       0.91      0.68      0.78      2604

    accuracy                           0.99    103687
   macro avg       0.95      0.84      0.89    103687
weighted avg       0.99      0.99      0.99    103687

TEST DATASET:
              precision    recall  f1-score   support

       False       0.98      1.00      0.99      4542
        True       0.76      0.43      0.55       155

    accuracy                           0.98      4697
   macro avg       0.87      0.71      0.77      4697
weighted avg       0.97      0.98      0.97      4697


#### Brown

single word:
              precision    recall  f1-score   support

       False       0.94      1.00      0.97     78010
        True       1.00      0.10      0.19      5285

    accuracy                           0.94     83295
   macro avg       0.97      0.55      0.58     83295
weighted avg       0.95      0.94      0.92     83295

+neighbors:
              precision    recall  f1-score   support

       False       0.98      1.00      0.99     78010
        True       0.95      0.69      0.80      5285

    accuracy                           0.98     83295
   macro avg       0.96      0.84      0.89     83295
weighted avg       0.98      0.98      0.98     83295

+case:
              precision    recall  f1-score   support

       False       0.99      1.00      0.99     78010
        True       0.93      0.79      0.85      5285

    accuracy                           0.98     83295
   macro avg       0.96      0.89      0.92     83295
weighted avg       0.98      0.98      0.98     83295

+lemma:
              precision    recall  f1-score   support

       False       0.99      1.00      0.99     78010
        True       0.93      0.79      0.85      5285

    accuracy                           0.98     83295
   macro avg       0.96      0.89      0.92     83295
weighted avg       0.98      0.98      0.98     83295

+POS:
              precision    recall  f1-score   support

       False       0.99      1.00      0.99     78010
        True       0.94      0.79      0.86      5285

    accuracy                           0.98     83295
   macro avg       0.96      0.89      0.92     83295
weighted avg       0.98      0.98      0.98     83295

+N-gram:
              precision    recall  f1-score   support

       False       0.99      1.00      0.99     78010
        True       0.94      0.79      0.86      5285

    accuracy                           0.98     83295
   macro avg       0.96      0.89      0.92     83295
weighted avg       0.98      0.98      0.98     83295

TEST DATASET:
              precision    recall  f1-score   support

       False       0.98      0.96      0.97      4542
        True       0.29      0.48      0.36       155

    accuracy                           0.94      4697
   macro avg       0.64      0.72      0.67      4697
weighted avg       0.96      0.94      0.95      4697
