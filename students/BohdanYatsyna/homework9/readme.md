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

зробив частину експериментів з параметрами

rougel требба викинути - негативна фіча

f_wer, f_sim_lema, f_sim_verb, f_syn

```
               precision    recall  f1-score   support 

contradiction       0.49      0.61      0.54      3237 
   entailment       0.65      0.60      0.62      3368 
      neutral       0.50      0.42      0.46      3219 

     accuracy                           0.54      9824 
    macro avg       0.55      0.54      0.54      9824 
 weighted avg       0.55      0.54      0.54      9824 
```
https://app.wandb.ai/yatsinaba/prj-nlp-2020-students_BohdanYatsyna_homework9/sweeps/komb4cnw?workspace=user-

ще трохи експериментів

https://app.wandb.ai/yatsinaba/prj-nlp-2020-students_BohdanYatsyna_homework9/sweeps/o871gaj7?workspace=user-yatsinaba

кращий результат
```
               precision    recall  f1-score   support 

contradiction       0.50      0.60      0.54      3237 
   entailment       0.67      0.61      0.64      3368 
      neutral       0.51      0.46      0.48      3219 

     accuracy                           0.56      9824 
    macro avg       0.56      0.55      0.55      9824 
 weighted avg       0.56      0.56      0.56      9824 
```

варі

для запуску ML программи один раз запустити ```text-entailment.py```

тут варіація моделей https://app.wandb.ai/yatsinaba/prj-nlp-2020-students_BohdanYatsyna_homework9/sweeps/gsuvmz3s?workspace=user-yatsinaba

найкращий результат 
```

               precision    recall  f1-score   support 

contradiction       0.51      0.61      0.55      3237 
   entailment       0.70      0.61      0.65      3368 
      neutral       0.52      0.49      0.50      3219 

     accuracy                           0.57      9824 
    macro avg       0.58      0.57      0.57      9824 
 weighted avg       0.58      0.57      0.57      9824 


```

NN реалізовуєтся на основі цього Decomposable Attention Model - https://arxiv.org/pdf/1606.01933.pdf
для запусуску нейромережевої версії ```nnsolution/__main__.py```


для запуску серії експериментів на wandb sweep для підбору фічей:
```
wandb sweep sweep_pc_feature_variation.yaml
wandb agent <generated link copied from console after pervious command>
```

для запуску серії експериментів на wandb sweep для підбору моделей:
```
wandb sweep sweep_pc_model_variation.yaml
wandb agent <generated link copied from console after pervious command>
```