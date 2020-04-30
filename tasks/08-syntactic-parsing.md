# Синтаксичний аналіз

## I. Покращення парсера залежностей

Візьміть за основу парсер залежностей, побудований на практичному занятті, і зробіть мінімум дві ітерації для покращення якості.

Варіанти покращення парсера:
* підберіть кращий набір ознак;
* зробіть класифікацію типів залежностей та поміряйте LAS (labelled attachment score);
* додайте операцію swap для опрацювання непроективних дерев;
* покращіть статичний оракул або замініть його недетермінованим чи динамічним оракулом;
* спробуйте інший класифікатор та зробіть оптимізацію гіперпараметрів;
* ваші ідеї.

За основу можна використати або свій парсер, або [приклад із заняття](../lectures/08-dep-parser-uk.ipynb).

Корисні посилання:
* [UD-корпус для української](https://github.com/UniversalDependencies/UD_Ukrainian-IU/)
* [Зручна бібліотека для роботи з форматом CoNLL](https://github.com/EmilStenstrom/conllu)
* Стаття з блогу Matthew Honnibal - [Parsing English in 500 Lines of Python](https://explosion.ai/blog/parsing-english-in-python)
* Книга про парсери залежностей - [Dependency Parsing by Kübler, McDonald, and Nivre](https://books.google.com.ua/books?id=k3iiup7HB9UC&pg=PA21&hl=uk&source=gbs_toc_r&cad=4#v=onepage&q&f=false)
* Гарний огляд типів парсера залежностей та оракулів - [Improvements in Transition Based Systems for Dependency Parsing](http://paduaresearch.cab.unipd.it/8004/1/Tesi.pdf)

## II. Використання парсера на нових даних

Виберіть кілька випадкових речень українською мовою на побудуйте дерева залежностей для них, використовуючи свій парсер.

Для токенізації можна використати https://github.com/lang-uk/tokenize-uk.

Для частиномовного аналізу можна використати https://github.com/kmike/pymorphy2. Зважте, що частиномовні теги в UD та в pymorphy2 відрізняються, зокрема pymorphy2 не розрізняє типи сполучників. Нижче подано спосіб вирівняти ці дві нотації:

```python
import pymorphy2

morph = pymorphy2.MorphAnalyzer(lang='uk')

DET = ['будь-який', 'ваш', 'ввесь', 'весь', 'все', 'всенький', 'всякий',
       'всілякий', 'деякий', 'другий', 'жадний', 'жодний', 'ин.', 'ін.',
       'інакший', 'інш.', 'інший', 'їх', 'їхній', 'її', 'його', 'кожний',
       'кожній', 'котрий', 'котрийсь', 'кілька', 'мій', 'наш', 'небагато',
       'ніякий', 'отакий', 'отой', 'оцей', 'сам', 'самий', 'свій', 'сей',
       'скільки', 'такий', 'тамтой', 'твій', 'те', 'той', 'увесь', 'усякий',
       'усілякий', 'це', 'цей', 'чий', 'чийсь', 'який', 'якийсь']

PREP = ["до", "на"]

mapping = {"ADJF": "ADJ", "ADJS": "ADJ", "COMP": "ADJ", "PRTF": "ADJ",
           "PRTS": "ADJ", "GRND": "VERB", "NUMR": "NUM", "ADVB": "ADV",
           "NPRO": "PRON", "PRED": "ADV", "PREP": "ADP", "PRCL": "PART"}

def normalize_pos(word):
    if word.tag.POS == "CONJ":
        if "coord" in word.tag:
            return "CCONJ"
        else:
            return "SCONJ"
    elif "PNCT" in word.tag:
        return "PUNCT"
    elif word.normal_form in PREP:
        return "PREP"
    elif word.normal_form in DET:
        return "DET"
    else:
        return mapping.get(word.tag.POS, word.tag.POS)
```

Запишіть ваші спостереження та результати в окремий файл.

### Оцінювання

80% - I. Покращення парсера залежностей  
20% - II. Використання парсера на нових даних

### Крайній термін

02.05.2020
