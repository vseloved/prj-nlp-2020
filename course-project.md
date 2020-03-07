## Теми курсових проєктів

### Проєкти від компаній

1. **ЛІГА:ЗАКОН** (українська мова)
   * Класифікація договорів за типами: https://paper.dropbox.com/doc/7CHgfH0P5yqIUtTI3GiFE
2. **Semantrum** (українська та російська мови)
   * Виправлення помилок у тексті, що отриманий в результаті роботи speech-to-text. Зразок тексту: https://www.speech.com.ua/index.html.
   * Розбиття speech-to-text розшифровки телеефіру на окремі сюжети. Зразок тексту: https://www.speech.com.ua/index.html.
   * Виділення сюжетів у потоці новин, кластеризація документів за сюжетом, або пошук подібних документів та дублікатів. Сюжет - це група статей, що повідомляють про одну й ту ж подію. Дані можна отримати з wikinews за конкретними пошуковими запитами, наприклад, за пошуком "Сирія".
   * Виявлення першоджерела новини, особливо для групи новин, які описують той самий сюжет.
   * Побудова хронології подій у новинах, пов’язаних із заданим об’єктом. Об’єктом може бути людина, компанія чи навіть коронавірус.
3. **ARVI Lab** (англійська мова)
   * Класифікація (або ранжування) речень у тексті за ознакою "show vs. tell": https://docs.google.com/document/d/1chSyzmzd1AtB04_MhkokcZdknMboJQ4JjY7cbet3mJA/edit?usp=sharing. Продовженням цієї задачі є генерація пояснень (див. приклади) чи перефразування з "tell" на "show".
4. **Biasless** (українська мова)
   * Визначення речень, які містять упередження за ознакою віку, статі, професії, кольору волосся, сексуальної орієнтації тощо: https://gist.github.com/khrystyna-skopyk/1c4a45cc05b1054493bf442ca0484bd8.

### Проєкти, для яких немає готових корпусів

Основна складність (і цікавість) цих проєктів в тому, що для них паралельно доведеться будувати і датасет, і модель. Більшість NLP-задач реального життя саме такі :)

1. Визначення зв’язків між сутностями на основі даних з Wikipedia, Freebase, DBPedia тощо.
2. Визначення суб’єктивних висловлювань у текстах новин.
3. Перетворення запитів людською мовою на SQL-запити і т.і.
4. Перевірка правопису для української мови. Дані можна проанотувати через LanguageTool; також схожий проєкт є [тут](https://github.com/khrystyna-skopyk/ukr_spell_check).
5. Автоматична генерація відповідей на запитання. (Дані можна брати з Вікіпедії чи https://ukrainian.stackexchange.com та інших SE сайтів).
6. Пошук плагіату в україномовних текстах. Дані можна видобувати на сайтах з рефератами, сайтах новин (передруківки).
7. Передбачення поширення неологізмів (сленгу чи жаргону) в соцмережих. (Є цікаве дослідження на цю тему: http://aclweb.org/anthology/C18-1135. Дані можна скрейпити з соцмереж).
8. Ведення дебатів; визначення аргументів "за" і "проти" у дебатах. Дані можна знайти в http://www.debatepedia.org.
9. Перекладач з діалектної української на літературну (і навпаки). Можна брати будь-який діалект України: львівську ґвару, подільський діалект, волинський діалект, лемківську мову, закарпатський говір, суржик тощо.
10. Генерація поезії. (Доступні дані: сайти з віршами, словники рим тощо).
11. Генерація мовних каламбурів.
12. Генерація тексту на задану тематику.
13. Визначення психотипу автора повідомлення. (Дані можна шукати у соцмережах, див. https://nlp.stanford.edu/courses/cs224n/2015/reports/6.pdf).

### Проєкти, для яких є готові корпуси

Передбачається, що якщо ви обрали один з цих проєктів, то ви будете шукати і використовувати додаткові дані, а не просто відтворювати вже готові результати.

1. Визначення тролінгу, пропаганди, образливих коментарів чи критики. Можна використати дані:
    - https://propaganda.qcri.org/nlp4if-shared-task/
    - https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge
    - https://www.kaggle.com/c/jigsaw-unintended-bias-in-toxicity-classification
    - https://www.kaggle.com/c/detecting-insults-in-social-commentary
    - https://www.kaggle.com/c/quora-insincere-questions-classification#description
    - https://sites.google.com/view/alw3/
    - https://sites.google.com/view/simah-2019/competition
    - http://poleval.pl/tasks/task6
2. Визначення подібності тексту чи перефразування тексту. Можна на основі новин зробити (різні ресурси часто перепощують ту саму інформацію іншими словами), а також використати дані:
    - https://www.kaggle.com/c/quora-question-pairs/data
    - http://alt.qcri.org/semeval2016/task1/
3. Визначення авторства чи визначення статі/віку/соціальної групи автора. Можна будь-яких авторів будь-якою мовою назбирати. Приклад даних: https://www.kaggle.com/c/spooky-author-identification.
4. Визначення емоцій/сентиментів для конкретного домену. Можна своїх даних наскрейпити зі споживацьких сайтів. Також є багато готових корпусів, наприклад, про емоції є тут:
    - https://competitions.codalab.org/competitions/17751
    - http://doraemon.iis.sinica.edu.tw/emotionlines/download.html
    - https://github.com/kj2013/claff-offmychest/
    - http://wndomains.fbk.eu/wnaffect.html 
5. Визначення найбільш ймовірного закінчення історії. Можна нагенерувати своїх даних з невеличких текстів, а також є https://competitions.codalab.org/competitions/15333.
6. Визначення значень слів. Є, наприклад, https://nlpub.github.io/russe-wsi-kit/.
7. Моделювання граматичних помилок, які роблять ті, хто вивчає мову:
    - https://sharedtask.duolingo.com/2018.html
8. Виправлення граматичних помилок, які роблять ті, хто вивчає мову:
    - https://www.cl.cam.ac.uk/research/nl/bea2019st/
    - https://sites.google.com/site/naistlang8corpora/
    - http://www.comp.nus.edu.sg/~nlp/conll14st.html
9. Визначення гумору, іронії, сарказму чи мовних каламбурів:
    - https://competitions.codalab.org/competitions/17468#learn_the_details
    - http://alt.qcri.org/semeval2017/task7/
    - http://www.alta.asn.au/events/sharedtask2019/description.html
    - http://www.amitavadas.com/Memotion.html
10. Автореферування тексту:
    - https://github.com/mahnazkoupaee/WikiHow-Dataset
11. Усунення гендерних/вікових/расових/тощо упереджень з даних та моделей NLP:
    - https://github.com/google-research-datasets/gap-coreference
    - https://arxiv.org/pdf/1805.04508.pdf
    - https://arxiv.org/pdf/1607.06520.pdf
12. Спрощення текстів:
    - https://newsela.com/data/ 
    - https://simple.wikipedia.org/wiki/Main_Page
    - https://sites.google.com/view/cwisharedtask2018 
13. Визначення рівня ввічливості тексту:
    - https://www.cs.cornell.edu/~cristian/Politeness.html
14. Побудова паралельного корпусу:
    - https://comparable.limsi.fr/bucc2017/bucc2017-task.html
15. Machine Comprehension using Commonsense Knowledge:
    - https://competitions.codalab.org/competitions/17184
16. POS-tagging для української мови з морфологічними ознаками:
    - https://github.com/UniversalDependencies/UD_Ukrainian-IU/tree/master
    - https://github.com/brown-uk/dict_uk
17. Навчи свого NLP-агента грати у “перевертня” (аналог нашої “мафії“):
    - https://aiwolfdial.kanolab.net/shared-task
18. Перевірка фактів на достовірність:
    - https://sites.google.com/view/clef2019-checkthat/

### Додаткові джерела даних та ідей

1. Гарна збірка NLP-задач зі статтями і даними:
    - https://github.com/Kyubyong/nlp_tasks
    - http://nlpprogress.com/
2. Діалоги з мультика "South Park":
    - https://www.kaggle.com/tovarischsukhov/southparklines
3. Корпуси пісень:
    - https://www.kaggle.com/mousehead/songlyrics
    - https://www.kaggle.com/gyani95/380000-lyrics-from-metrolyrics
4. Відгуки про сорти вин та їжу:
    - https://www.kaggle.com/zynicide/wine-reviews
    - https://www.kaggle.com/snap/amazon-fine-food-reviews
5. SMS-спам:
    - http://www.dt.fee.unicamp.br/~tiago/smsspamcollection/
6. Питання та відповіді:
    - https://github.com/google-research-datasets/tydiqa
7. Корпус мови ненависті та заспокійливих відповідей на ці образливі коментарі:
    - https://github.com/marcoguerini/CONAN
8. Українськомовні корпуси:
    - https://www.facebook.com/groups/488552241633414/permalink/489448364877135/
    - https://data.gov.ua/dataset
9. Додаткові джерела даних:
    - змагання CONLL: http://www.conll.org/previous-tasks
    - змагання SemEval: http://alt.qcri.org/semeval2020/index.php?id=tasks (див. також попередні роки)
    - https://datasetsearch.research.google.com/
    - https://catalog.ldc.upenn.edu/
    - https://quantumstat.com/dataset/dataset.html
    - https://www.datasetlist.com/
    - https://www.kaggle.com/datasets?sortBy=relevance&group=featured&page=1&pageSize=20&size=all&filetype=all&license=all&tagids=11208
    - http://noisy-text.github.io/
