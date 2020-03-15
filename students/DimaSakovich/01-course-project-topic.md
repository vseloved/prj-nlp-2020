## Phoneme based speech2text system with custom language model for Russian and Vietnamese *

\* if it will be enough time, QA module will be added

### Reason:
Vietnamese asr is one of my tasks on my current job. But plain asr is not interesting, so I would like to extend this
task by extracting main sense from decoded text, especially when it wasn't well decoded. That's why I want to do it 
also for Russian. The reason why not Ukrainian - almost no available speech corpus. But, these languages are pretty
similar in sense of pronunciation, so maybe it will be possible to make multi-language model.


### Problems to solve

##### Grapheme To Phoneme Conversion
  * required for better speech recognition
  * ****`PAPER`**** [Grapheme-to-Phoneme Models for (Almost) Any Language](https://pdfs.semanticscholar.org/b9c8/fef9b6f16b92c6859f6106524fdb053e9577.pdf)
  * ****`PAPER`**** [Polyglot Neural Language Models: A Case Study in Cross-Lingual Phonetic Representation Learning](https://arxiv.org/pdf/1605.03832.pdf)
  * ****`PAPER`**** [Multitask Sequence-to-Sequence Models for Grapheme-to-Phoneme Conversion](https://pdfs.semanticscholar.org/26d0/09959fa2b2e18cddb5783493738a1c1ede2f.pdf)
  * ****`PROJECT`**** [Sequence-to-Sequence G2P toolkit](https://github.com/cmusphinx/g2p-seq2seq)
  * ****`PROJECT`**** [g2p_en: A Simple Python Module for English Grapheme To Phoneme Conversion](https://github.com/kyubyong/g2p) 
  * ****`DATA`**** [Multilingual Pronunciation Data](https://drive.google.com/drive/folders/0B7R_gATfZJ2aWkpSWHpXUklWUmM)
  
##### Language modeling
  * part of speech recognition system
  * some info can be found [here](http://nlpprogress.com/english/language_modeling.html)
  * depends on chosen asr system, kenLM can be used for training language model
  * further investigation need to be done in the near future

##### Speech recognition
  * ****`kaldi`**** or ****`wav2letter++`****  framework will be used, due to it provides best results
  * implement one of the architectures from here [wer_are_we](https://github.com/syhw/wer_are_we)
  
Data:

Vietnamese speech corpus:
1. https://catalog.ldc.upenn.edu/LDC2017S01
2. https://ailab.hcmus.edu.vn/vivos

Russian speech corpus:
1. https://towardsdatascience.com/russian-open-speech-to-text-stt-asr-dataset-4c4e5d6a292c
 
  
##### Question answering
This task should be done only if it will be enough time.

Question-answering is a deep and wide problem, which I would like to dig deeper. 
In case of this project it will be applied to speech text to get answers on basic questions.

For russian language I can use:
http://nlpprogress.com/russian/question_answering.html

For vietnamese:
https://github.com/mailong25/bert-vietnamese-question-answering

in both cases I suppose Wikipedia corpus also can be useful
