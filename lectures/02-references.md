## Корисні посилання

### Бібліотеки

Найбільш підтримувані та розвинені:
- [Spacy](https://spacy.io/) (7 languages; Python)
- [StanfordNLP](https://stanfordnlp.github.io/stanfordnlp/) (53 languages; Python)
- [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) (6 languages; Java + wrappers for 10+ programming languages)
- [Emory NLP](https://github.com/emorynlp/) (English; Java)
- [OpenNLP](https://opennlp.apache.org/) (7 languages; Java)
- [AllenNLP](https://allennlp.org/) (English; Python)

При роботі зі spaCy рекомендуємо використовувати моделі середнього розміру, наприклад, en_core_web_md.

Навчальні:
- [nltk](http://www.nltk.org/) (English; Python)
- [TextBlob](http://textblob.readthedocs.io/en/dev/) (English; Python)
- [cl-nlp](https://github.com/vseloved/cl-nlp) (Common Lisp)

Для української мови:
- [lang-uk](https://github.com/lang-uk) (Python)
- [pymorphy2](https://github.com/kmike/pymorphy2) (Python)
- [nlp_uk](https://github.com/brown-uk/nlp_uk) (Groovy)
- [StanfordNLP](https://stanfordnlp.github.io/stanfordnlp/) (Python)

Установити pymorphy2 для української мови можна так:
```sh
pip install git+https://github.com/kmike/pymorphy2.git pymorphy2-dicts-uk
```

Стеммер:
- [SnowballStem](http://snowballstem.org/download.html) (English, Russian, and 16 more languages)

Демки:
- [Ukr stemmer](http://www.senyk.poltava.ua/projects/ukr_stemming/demo.html)
- [Stanford syntactic parsers](http://nlp.stanford.edu:8080/parser/)
- [spaCy dependency parser](https://explosion.ai/demos/displacy)
- [AllenNLP demos](https://demo.allennlp.org/)
- [Cognitive Computation Group semantic role labeling](http://cogcomp.org/page/demo_view/srl)

### Нотація частин мови та зв'язків залежностей

Universal:
- [Universal POS tags](http://universaldependencies.org/u/pos/index.html)
- [Universal POS features](http://universaldependencies.org/u/feat/index.html)
- [Universal dependencies v2](http://universaldependencies.org/docs/en/dep/)

Penn:
- [Penn Treebank POS tags](https://sites.google.com/site/partofspeechhelp/)
- [Penn Treebank phrase labels](http://www.surdeanu.info/mihai/teaching/ista555-fall13/readings/PennTreebankConstituents.html)

Clear (a.k.a. Emory, used by spaCy):
- [Guidelines for the Clear Style Constituent to Dependency Conversion](http://www.mathcs.emory.edu/~choi/doc/cu-2012-choi.pdf)

Stanford:
- [Original Stanford dependencies](https://nlp.stanford.edu/software/dependencies_manual.pdf)
- [Universal Stanford dependencies](https://nlp.stanford.edu/pubs/USD_LREC14_paper_camera_ready.pdf)

Для української мови:
- [pymorphy2 POS](https://pymorphy2.readthedocs.io/en/latest/user/grammemes.html)
- [Languagetool POS](https://github.com/brown-uk/dict_uk/blob/master/doc/tags.txt)

### Мовні ресурси

Словники української мови:
- [СУМ](http://sum.in.ua/)
- [Словники України](http://lcorp.ulif.org.ua/dictua/)

WordNet та інші мережі на основі WordNet:
- [WordNet](https://wordnet.princeton.edu/) and [WordNet online search](http://wordnetweb.princeton.edu/perl/webwn)
- [SentiWordNet](https://github.com/aesuli/sentiwordnet)
- [FrameNet](https://framenet.icsi.berkeley.edu/fndrupal/frameindex)
- [PropBank](https://propbank.github.io/)
- [ConceptNet](http://conceptnet.io/)
- [VerbNet](https://verbs.colorado.edu/~mpalmer/projects/verbnet.html)
- [ImageNet](http://www.image-net.org/)

Abstract Meaning Representation:
- [Abstract Meaning Representation](https://amr.isi.edu/language.html)

### Більше про структурну лінгвістику

Морфологія:
- http://www.ling.upenn.edu/courses/Fall_1998/ling001/morphology1.html
- http://www.ling.upenn.edu/courses/Fall_1998/ling001/morphology2.html
- http://www.cis.uni-muenchen.de/~fraser/morphology_2016/Inflection_Derivation.pdf

Синтаксиc:
- https://en.wikipedia.org/wiki/Parse_tree
- http://www.aclweb.org/anthology/W15-2128
- http://www.linguisticsnetwork.com/syntactic-constituency/

Конференція [Dependency Linguistics](http://depling.org/) - гарне джерело статей про опрацювання синтаксичних структур різних мов різними методами.

Speech and Language Processing by Dan Jurafsky and James H. Martin:
- [8. Part-of-speech Tagging](https://web.stanford.edu/~jurafsky/slp3/8.pdf)
- [12. Constituency Grammars](https://web.stanford.edu/~jurafsky/slp3/12.pdf)
- [15. Dependency Parsing](https://web.stanford.edu/~jurafsky/slp3/15.pdf)
- [19. Word senses and WordNet](https://web.stanford.edu/~jurafsky/slp3/19.pdf)
- [20. Semantic Role Labeling](https://web.stanford.edu/~jurafsky/slp3/20.pdf)

NLP with Python:
- [3. Processing Raw Text](http://www.nltk.org/book/ch03.html)
- [5. Categorizing and Tagging Words](http://www.nltk.org/book/ch05.html)
- [8. Analyzing Sentence Structure](http://www.nltk.org/book/ch08.html)
- [WordNet Interface](http://www.nltk.org/howto/wordnet.html)
