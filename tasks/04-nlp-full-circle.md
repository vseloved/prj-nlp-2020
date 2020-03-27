# Повний цикл NLP-проєкту

## I. Перевірка фактів на достовірність

У межах цієї задачі ви побудуєте систему видобування фактів на правилах, а також інструменти для оцінювання якості роботи цієї системи.

### 1. Домен

Виберіть домен, для якого можна побудувати невелику базу даних на основі [DBPedia](https://dbpedia.org/sparql). База даних повинна містити хоча б три колонки з даними. Приклади доменів:
- актори, фільми, в яких вони знімались, та роки випуску фільмів;
- письменники, книжки, які вони написали, та роки виходу книжок;
- музичні гурти і їхні учасники/концерти/альбоми з роками діяльності/випуску;
- компанії та всі їхні CEO/CTO з роками діяльності;
- люди і всі їхні місця роботи з часовими проміжками;
- політики і політичні партії, в яких вони брали участь, з роками діяльності;
- спортсмени і їхні команди, матчі, титули тощо з інформацією про місце/дату/рахунок матчів.

Проаналізуйте домен і напишіть SPARQL-запит для побудови бази даних.

Посібник по SPARQL від Cambridge Semantics:
1. <https://www.cambridgesemantics.com/blog/semantic-university/learn-sparql/>
2. <https://www.cambridgesemantics.com/blog/semantic-university/learn-sparql/sparql-nuts-bolts/>
3. <https://www.cambridgesemantics.com/blog/semantic-university/learn-sparql/sparql-by-example/>

### 2. Видобування фактів

2.1. Напишіть програму, яка шукає статті у Вікіпедії про сутності, що належать до вашого домена, та витягає тексти цих статей.

2.2. Напишіть програму, яка опрацьовує текст статті (саме сирий текст, а не таблички, якщо такі є) та витягає з нього інформацію про ваш домен. Цю інформацію ви будете порівнювати зі сформованою базою даних.

### 3. Оцінювання результатів

Розробіть метрику, яка покаже, наскільки інформація, яку ви дістали зі статей, збігається з інформацією в вашій базі даних. Скільки пропущеної інформації? Чи є часткові збіги? (Наприклад, ім'я СЕО певної компанії збігається лише частково або ім'я СЕО збігається, а роки діяльності різні.)

Додайте ваші спостереження і висновки.

### Приклад

1. Формуємо базу даних про фільми, що знімав Вуді Аллен.

Пишемо SPARQL-запит, щоб отримати всі фільми Вуді Аллена, роки їх випуску (якщо вказано) та акторів, які там знімались:
```
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX res:  <http://dbpedia.org/resource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?uri ?movie ?year ?star
WHERE {
        ?uri dbo:director res:Woody_Allen .
        ?uri rdfs:label ?movie .
        FILTER (lang(?movie) = 'en')
        OPTIONAL {?uri dct:subject ?cat . 
                  ?cat rdfs:label ?year . 
                  FILTER (regex (?year, '\\d+ films', 'i'))} .
        ?uri dbo:starring ?staruri .
        ?staruri rdfs:label ?star .
        FILTER (lang(?star) = 'en')
}
```

Результатом буде таблиця на чотири колонки та 336 рядків:
```
uri                                                 	movie                   	year    	star
http://dbpedia.org/resource/Everyone_Says_I_Love_You	Everyone Says I Love You	1996 films	Goldie Hawn
http://dbpedia.org/resource/Celebrity_(film)        	Celebrity (film)        	1998 films	Leonardo DiCaprio
http://dbpedia.org/resource/Everyone_Says_I_Love_You	Everyone Says I Love You	1996 films	Natalie Portman
http://dbpedia.org/resource/Celebrity_(film)        	Celebrity (film)        	1998 films	Winona Ryder
http://dbpedia.org/resource/What's_Up,_Tiger_Lily%3F	What's Up, Tiger Lily?  	1966 films	Woody Allen
http://dbpedia.org/resource/Sleeper_(1973_film)     	Sleeper (1973 film)     	1973 films	Woody Allen
http://dbpedia.org/resource/Celebrity_(film)        	Celebrity (film)        	1998 films	Bebe Neuwirth
http://dbpedia.org/resource/Hannah_and_Her_Sisters  	Hannah and Her Sisters  	1986 films	Lloyd Nolan
http://dbpedia.org/resource/Hannah_and_Her_Sisters  	Hannah and Her Sisters  	1986 films	Maureen O'Sullivan
http://dbpedia.org/resource/Crimes_and_Misdemeanors 	Crimes and Misdemeanors 	1989 films	Sam Waterston
...
```

Чистимо результат від зайвої інформації: наприклад, треба видалити "films" після років і "(film)" з назв фільмів. Зберігаємо ці дані у зручному форматі.

2.1. Скрейпимо інформацію зі сторінок Вікіпедії:
- зі сторінки режисера <https://en.wikipedia.org/wiki/Woody_Allen>;
- зі сторінок фільмів — відрізаємо останню частину від URI фільму (перша колонка) і доклеюємо до "https://en.wikipedia.org/wiki/";
- можна також зберігати URI акторів і скейпити їхні сторінки на Вікіпедії.

2.2. Пишемо набір правил (за допомогою NER, частин мови, синтаксичних дерев, регекспів тощо), які витягають потрібну нам інформацію з тексту:

```
Allen directed, starred in, and co-wrote (with Mickey Rose) Take the Money and Run in 1969, which received positive reviews...

Also in 1996, Portman had brief roles in Woody Allen's musical Everyone Says I Love You and Tim Burton's comic science fiction film Mars Attacks!.

DiCaprio played a self-mocking role in a small appearance in Woody Allen's caustic satire of the fame industry, Celebrity (1998) whom Bilge Ebiri labelled "the best thing in the film".
```

3. Розробляємо метрику, оцінюємо результат і намагаємось покращити якість. Пишемо спостереження і висновки.

## II. Курсовий проєкт

Для свого курсового проєкту визначте остаточні метрики і напишіть програму, яка їх реалізує. Покажіть приклад роботи програми на іграшкових даних (до 10 прикладів реальних чи штучних даних).

### Оцінювання

- 80% - перевірка фактів
- 20% - курсовий проєкт

## Крайній термін

04.04.2020
