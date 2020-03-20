Train my own conversational model!

Choose an approach and implement it.

It's hard to evaluate the conversation quality objectively. Maybe I should take some popular chat bot as a baseline and try to obtain a comparable quality. Also, I'm expenting course mentors to provide me with some good for a set of questions and a set of aspects for evaluation.

Following approaches is considered:

1. Generative model: n-gram language model.

Simple and good approach to language modeling. It's counting n-grams and smoothing probabilities. Model should be trained on dialogue data. I'll fallback to this if fail with other approaches.

2. Generative model: LSTM-based language model.

It will take some time to train such a model. Also considered character-based models. Will base development on this [blogpost by Karpathy](http://karpathy.github.io/2015/05/21/rnn-effectiveness/).

3. Conditional language modeling: seq2seq model.

The "right" (and also the most ambitious) way to implement a conversational chat-bot. For what I've read so far, generating language is a complicated task, so I might need days of CPU time or hours of GPU time to train the model. Probably would have to buy a GPU or order one, e.g. on AWS.

Generally, I will use encoder-decoder-attention architecture, but I need help from mentors on deciding on specific details of the architecture and tune hyperparameters. I will take [this seq2seq bot](https://github.com/Conchylicultor/DeepQA) as a reference point. Also, there are ton of other implementation on Github.

4. Selective model: embeddings-based ranking.

One more way to tackle the problem is to build a ranking system that scores predefined replicas (e.g. from Twitter) given the question. For this approach, I need to learn unsupervised sentence embeddings (e.g. sent2vec) on dialogue corpus or use question-answer pairs to train supervised embeddings (e.g. StarSpace). Then score all possible answers and reply with the most similar one. 

5. Selective model: DSSM.

There is also a popular way to build a supervised ranking system, called Deep Structures Semantic Model (DSSM). I have no understanding of it so far, if I'd be able to find some help from course mentors that would be great. Planning to start studying it from [this presentation](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/CIKM14_tutorial_HeGaoDeng.pdf).

Dialogue data to train the models:

Choosing the right dataset (as I've learned on our first online lecture :P) to train my chat-bot can make a big difference. There are a few options that I can utilize:

>[Cornell Movie Dialogs](http://www.cs.cornell.edu/%7Ecristian/Cornell_Movie-Dialogs_Corpus.html) - small corpus of dialogues from English movies.
>[OpenSubtitles](http://opus.nlpl.eu/OpenSubtitles.php) - bigger corpus of English subtitles (but also noisier).

Also need to explore what kind of datasets I can use from [here](https://github.com/Conchylicultor/DeepQA#presentation).

More useful links on chat-bots:

>WildML posts: [part1](http://www.wildml.com/2016/04/deep-learning-for-chatbots-part-1-introduction/) (overview) and [part2](www.wildml.com/2016/07/deep-learning-for-chatbots-2-retrieval-based-model-tensorflow/) (retrieval-based)
>Stanford [slides](http://web.stanford.edu/class/cs20si/lectures/slides_13.pdf) on TensorFlow seq2seq chat-bot