## Logistic Regression:
              precision    recall  f1-score   support

        left       0.86      0.87      0.86      6371
      reduce       0.85      0.78      0.81      6875
       right       0.75      0.79      0.77      5996
       shift       0.85      0.87      0.86      6578

    accuracy                           0.83     25820
   macro avg       0.83      0.83      0.83     25820
weighted avg       0.83      0.83      0.83     25820

-> correct: 8717 out of 12574

## Feature Extraction Improvement & Logistic Rergression:
        left       0.94      0.95      0.94      6371
      reduce       0.90      0.85      0.88      6875
       right       0.80      0.83      0.82      5996
       shift       0.87      0.87      0.87      6578

    accuracy                           0.88     25820
   macro avg       0.88      0.88      0.88     25820
weighted avg       0.88      0.88      0.88     25820

-> correct: 9735 out of 12574

## Feature Extraction Improvement & XGBoost:
              precision    recall  f1-score   support

        left       0.94      0.96      0.95      6371
      reduce       0.93      0.85      0.89      6875
       right       0.82      0.88      0.85      5996
       shift       0.89      0.89      0.89      6578

    accuracy                           0.89     25820
   macro avg       0.89      0.89      0.89     25820
weighted avg       0.90      0.89      0.89     25820

-> І хоча XGBoost використовує всі ядра на відміну від логістичної регресії, але predict займає цілу вічність, тож результат не є адекватним.

## Adhoc Oracle & Logistic Regression:
              precision    recall  f1-score   support

        left       0.93      0.95      0.94      6371
      reduce       0.90      0.86      0.88      6875
       right       0.80      0.84      0.82      5996
      right2       0.81      0.84      0.82      1265
       shift       0.83      0.81      0.82      5313

    accuracy                           0.86     25820
   macro avg       0.85      0.86      0.86     25820
weighted avg       0.87      0.86      0.86     25820


-> correct: 9771 out of 12574
LAS: 77.7%
Не зважаючи на нижчий f1-score модель краще вгадує зв'язки.