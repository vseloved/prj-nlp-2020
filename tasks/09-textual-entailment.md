# Логічне слідування

## Завдання

Розробіть класифікатор, який приймає на вхід текст та гіпотезу і визначає зв'язок між ними за трьома класами:
- entailment (гіпотеза логічно слідує з тексту)
- contradiction (гіпотеза суперечить тексту)
- neutral (гіпотеза і текст не пов'язані)

Побудуйте базове рішення та ітеративно покращуйте його, додаючи ознаки. Обов'язково випробуйте ознаки лексичної, граматичної та семантичної схожості:
* До ознак *лексичної схожості* належить частка сутностей, слів, енграмів, іменників, дієслів, числівників тощо, які перетинаються в тексті та гіпотезі. Спробуйте лематизацію чи стемінг, опрацюйте заперечення, нормалізуйте дані.
* До ознак *граматичної схожості* належить частка синтаксичних структур чи залежностей, які перетинаються в тексті та гіпотезі. Спробуйте або дерева складників, або дерева залежностей, або і те, і друге.
* До ознак *семантичної схожості* належить:
  1. Наявність лексико-семантичних зв'язків між словами в тексті та в гіпотезі. Спробуйте виявити наявність синонімів, антонімів, гіперонімів, гіпонімів, пов'язаних слів, логічного слідування тощо. Ви можете використати будь-яку онтологію ([WordNet](https://wordnet.princeton.edu/), [ConceptNet](http://conceptnet.io/), [BabelNet](https://babelnet.org/) тощо) та будь-яку бібліотеку для роботи з нею.
  2. *[Опційно]* Схожість семантичних ролей в тексті та гіпотезі. Спробуйте готові рішення для маркування семантичних ролей у тексті та гіпотезі (наприклад, [AllenNLP SRL](https://github.com/masrb/allenNLP-SRL) чи [AMR Eager](https://cohort.inf.ed.ac.uk/amreager.html)).

Корисні статті, у яких можна підглянути ознаки:
- [Feature Analysis for Paraphrase Recognition and Textual Entailment](https://pdfs.semanticscholar.org/2d7d/f0b5ac15cdaa50928031f5bb2fc63a0a1f68.pdf), 2013
- [Machine Learning Experiments for Textual Entailment](http://u.cs.biu.ac.il/~nlp/RTE2/Proceedings/02.pdf), 2006
- [A large annotated corpus for learning natural language inference](https://nlp.stanford.edu/pubs/snli_paper.pdf), 2015
- [Learning to recognize features of valid textual entailments](https://nlp.stanford.edu/pubs/rte-naacl06.pdf), 2006
- [Textual entailment](http://www.lsi.upc.edu/~ageno/anlp/textualEntailment.pdf), 2014

Для тренування та тестування використайте **train** та **dev** частини з [The Stanford Natural Language Inference (SNLI) Corpus](https://nlp.stanford.edu/projects/snli/). Протестуйте фінальне рішення на **test**-частині корпусу.

Запишіть ваші спостереження та результати в окремий файл.

## Оцінювання

100% за завдання.

## Крайній термін

09.05.2020
