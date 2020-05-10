## Project data sources

There are so many tasks and data source so it's not clear which one should be attached as part of task

### Speech2text data

#### Vietnamese

* https://catalog.ldc.upenn.edu/LDC2017S01

3.3 Gb of recorded mobile phone talks. They says that there are 201 hours, but actually there are only 23
Audio quality is low, most of records contain noise. Records are stored in *.sph format.

* https://ailab.hcmus.edu.vn/vivos

1.4 Gb of clean speech, recorded by 65 unique speakers, males and females. Records have no noise, recorded with 
good microphone, stored in *.wav format.

#### Russian

* https://habr.com/ru/post/474462/
* https://github.com/snakers4/open_stt

There are tons of data, some of them I already downloading. Also, I already filled the application form to get full
access to the data. It's hard to say right now how good as the data. At least, there is a lot of it.

### G2P

#### Vietnamese

g2p mapping can be downloaded from here
https://sourceforge.net/projects/vietnamese-grapheme-to-phoneme/files/latest/download

#### Russian

g2p mapping will be created manually. God bless in russian almost all words are pronounced as well as read. 
Exception is soft consonants.

### Text data for LM

#### Vietnamese

* utterances from stt data
* reddit threads for natural language data
* wikipedia dump for formal data

#### Russian

* utterances from stt data
* reddit threads for natural language data
* wikipedia dump for formal data

### QnA

#### Vietnamese

https://github.com/mailong25/bert-vietnamese-question-answering

json data with question text paragraphs and answer.
In some cases paragraphs are mapped to some id. Should be further investigated


#### Russian

* http://nlpprogress.com/russian/question_answering.html

data can be downloaded from here:
https://github.com/sberbank-ai/data-science-journey-2017/tree/master/problem_B


## Project data labeling

For russian speech data there are enough data. 

For vietnamese speech data I already prepared 10 hours dataset which consist of my company's call-centres recordings. 
But due the fact that these recording may contain some debtor's personal data, there are no option to outsource this work. 
So, the records will be transcribed by vietnamese employees. Currently, there are no information how many annotators 
will be and when they will be ready to start. it should be solved by management on the next week.  
To improve annotation quality, I already preprocessed recordings to make sure that each recording is one utterance,
reduced noise level and silence gaps.  
In the perfect world the instructions will be the next:
* for each annotator prepare subset of data, each subset has common records
* annotator have to fill the excel table where 1st column is file_name, 2nd is text transcription
* calculate WER for common records to evaluate annotation quality