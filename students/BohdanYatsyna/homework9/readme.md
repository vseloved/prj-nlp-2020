перший  бейзлайн прогнав тільки з однією ффічею - jacard similarity by lema

вийшло так
https://app.wandb.ai/yatsinaba/prj-nlp-2020-bogdan-students_BohdanYatsyna_homework9/runs/izlj3wm0
```
               precision    recall  f1-score   support

contradiction       0.41      0.68      0.51       648
   entailment       0.48      0.53      0.50       648
      neutral       0.37      0.09      0.15       668

     accuracy                           0.43      1964
    macro avg       0.42      0.43      0.39      1964
 weighted avg       0.42      0.43      0.39      1964
```

додавання TD-IDF в пайплайн однозначно погіршувало результат до ```accuracy = 0.33```

додав нормалізацію, видалив стоп слова

added verbs and removed stop words




також в раках цього завдання я намагався зробити ефективним опрацювання данних ( потоки, spacy pipe)
та зробив в wandb перебір моделей з параметрами 

для запуску программи один раз запустити ```text-entailment.py```

для запуску серії експериментів на wandb sweep:
```
wandb sweep sweep.yaml
wandb agent <generated link copied from console after pervious command>
```