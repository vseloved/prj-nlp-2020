## Speech summarization and sentiment system for Vietnamese and Russian

### Reason:
Vietnamese asr is one of my tasks on my current job. But plain asr is not interesting, so I would like to extend this
task by extracting main sense from decoded text, especially when it wasn't well decoded. That's why I want to do it 
also for Russian. The reason why not Ukrainian - almost no available speech corpus. But, these languages are pretty
similar in sense of pronunciation, so maybe it will be possible to make multi-language model. Solving this problem can
be further extended in making a simple voice assistant

### Data:
Vietnamese speech corpus:
1. https://catalog.ldc.upenn.edu/LDC2017S01
2. https://ailab.hcmus.edu.vn/vivos

Russian speech corpus:
1. https://towardsdatascience.com/russian-open-speech-to-text-stt-asr-dataset-4c4e5d6a292c

Vietnamese sentiment corpus:
1. https://github.com/undertheseanlp/NLP-Vietnamese-progress/blob/master/tasks/sentiment_analysis.md

Russian sentiment corpus:
1. https://www.kaggle.com/c/sentiment-analysis-in-russian/data

In case of sentiment, it's always can be scrapped some more data from web

For summarization I didn't find some relevant data sources right now


### Problems to solve

##### Grapheme To Phoneme Conversion
  * required for better speech recognition
  * ****`PAPER`**** [Grapheme-to-Phoneme Models for (Almost) Any Language](https://pdfs.semanticscholar.org/b9c8/fef9b6f16b92c6859f6106524fdb053e9577.pdf)
  * ****`PAPER`**** [Polyglot Neural Language Models: A Case Study in Cross-Lingual Phonetic Representation Learning](https://arxiv.org/pdf/1605.03832.pdf)
  * ****`PAPER`**** [Multitask Sequence-to-Sequence Models for Grapheme-to-Phoneme Conversion](https://pdfs.semanticscholar.org/26d0/09959fa2b2e18cddb5783493738a1c1ede2f.pdf)
  * ****`PROJECT`**** [Sequence-to-Sequence G2P toolkit](https://github.com/cmusphinx/g2p-seq2seq)
  * ****`PROJECT`**** [g2p_en: A Simple Python Module for English Grapheme To Phoneme Conversion](https://github.com/kyubyong/g2p) 
  * ****`DATA`**** [Multilingual Pronunciation Data](https://drive.google.com/drive/folders/0B7R_gATfZJ2aWkpSWHpXUklWUmM)

##### Speech recognition
  * ****`kaldi`**** framework will be used, due to it provides best results
  * implement one of the architectures from here [wer_are_we](https://github.com/syhw/wer_are_we)
  
##### Sentiment analysis
  * of course such libraries like ``Polyglot`` can detect text sentiment. But in case of Vietnamese, it can only define
  the sentiment of each separate word. Such approach, when we averaging word polarity through sentence doesn't seem to me
  to be good enough
  
##### Keyword extraction
  * after speech recognition I would like to extract key information from it
  * maybe custom NER will be enough, I don't know
