import random
from nltk.tokenize import sent_tokenize, word_tokenize

import string
import re
from typing import List


class DatasetGenerator:

    def generate(self, data: List[str]):
        result = []
        for data_line in data:
            result += self.generate_for_text(data_line)
        return result

    def generate_for_text(self, text: str):
        sentences = sent_tokenize(text)

        size = len(sentences)
        start = 0
        result = []
        i = 0
        while i < size:
            num_of_sents = self.get_random_num_of_sentences()
            end = i + num_of_sents if i + num_of_sents < len(sentences) else size

            data = self.generate_data_for_sentences(sentences[i:end])
            i = end

            result.append(data)

        return result

    def generate_data_for_sentences(self, sentences: List[str]):

        result = []
        sentences_size = len(sentences)
        for i in range(0, sentences_size):

            sent_data = []
            tokens = word_tokenize(sentences[i])
            tokens_size = len(tokens)
            should_set_end_word = False
            for j in range(tokens_size - 1, -1, -1):
                token = tokens[j]
                if self.__is_punctuation(token):
                    if j == tokens_size - 1 and i < sentences_size - 1:
                        should_set_end_word = True
                    else:
                        sent_data.insert(0, [token, False])
                    continue

                word = self.__randomly_lowercase_word(token, word_idx=j, sent_idx=i)

                if should_set_end_word:
                    sent_data.insert(0, [word, True])
                    should_set_end_word = False
                else:
                    sent_data.insert(0, [word, False])

            result += sent_data

        return result

    def __randomly_lowercase_word(self, word: str, word_idx: int, sent_idx: int):
        if sent_idx == 0 or word_idx > 0:
            return word

        should_be_lower = random.choice([True, False])
        if should_be_lower:
            return word.lower()

        return word

    def __is_punctuation(self, token: str):
        if token in string.punctuation:
            return True
        return False

    def __is_end_word_in_sent(self, word: str, word_idx: int, num_token_in_sents: int):
        if self.word_pattern.match(word) is None:
            return False

        if word_idx == num_token_in_sents - 1:
            return True

    def get_random_num_of_sentences(self):
        num = random.choices([1, 2, 3, 4], weights=[1, 12, 4, 3], k=1)[0]
        return num


dataset_generator = DatasetGenerator()


text = "Suicide won't oure shyness problems.  [Headline over Beth Winship's teen-advice column, Morning Union , Springfield, (Massachusetts), .  Submitted by .]"


result = dataset_generator.generate(text)

print(result)
