## Speech summarization and sentiment system for Vietnamese and Russian
The idea is to build speech recognition system that will process natural language. Key problem, that we can face here is
that languages we are building it has not so many free available data to train asr, so not always decoded text will be
the same what person said. In a future, such system can be improved for making voice assistant.

More details and possibility of implementing such project should be discussed with Mariana/Seva


Problems to solve:

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
  
##### Text summarization
  * after speech recognition I would like to summarize text to extract key information from it
  * maybe custom NER will be enough, I don't know
