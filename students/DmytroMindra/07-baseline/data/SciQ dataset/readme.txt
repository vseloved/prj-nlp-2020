SciQ is a dataset of Science Questions, available at http://data.allenai.org/sciq/. It consists of 13679 human-generated multiple-choice questions inspired by short text snippets from science textbooks.


Dataset split size:
11679 training instances
1000 validation instances
1000 test instances


The questions in SciQ were composed by crowdworkers who were instructed to write a question based on short supporting text snippets from a science text book. The dataset creation process is described in detail in the paper [1].


There are two settings in which SciQ can be used:

i) as a Reading Comprehension dataset, where the goal is to answer the question given the supporting document
ii) as a Multiple Choice QA dataset, where the goal is to choose the correct option given any material available.


The majority of questions comes with the supporting text snippet (10481 in train, 887 in validation, and 884 in test). However, some questions were obtained from unreleasable texts. For these, the string with the supporting document is empty and setting i) excludes these examples.


For questions, feedback or comments, please reach out to one of the authors:

j.welbl@cs.ucl.ac.uk
nfliu@cs.washington.edu
mattg@allanai.org



[1] ’Crowdsourcing Multiple Choice Science Questions’ by Johannes Welbl, Nelson F. Liu, Matt Gardner, Workshop on Noisy User-Generated Text 2017.  http://noisy-text.github.io/2017/pdf/WNUT13.pdf


@InProceedings{welbl2017crowdsourcing,
  author    = {Welbl, Johannes  and  Liu, Nelson F.  and  Gardner, Matt},
  title     = {Crowdsourcing Multiple Choice Science Questions},
  booktitle = {Proceedings of the Third Workshop on Noisy User-generated Text},
  year      = {2017},
  address   = {Copenhagen, Denmark},
  publisher = {Association for Computational Linguistics},
  pages     = {},
  url       = {http://noisy-text.github.io/2017/pdf/WNUT13.pdf}
}
