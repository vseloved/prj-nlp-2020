import unittest
import spacy

from headlines.formatting.formatting import process_single_word, capitalize_alpha

nlp = spacy.load('en_core_web_md')


class SeparateWordProcessingTestCases(unittest.TestCase):

    def test_first_word_capitalized(self):
        source = "ho"
        expected = "Ho"
        tokens = nlp(source)
        result = process_single_word(tokens, True, False, False)
        self.assertEqual(expected, result)

    def test_last_word_capitalized(self):
        source = "ho"
        expected = "Ho"
        tokens = nlp(source)
        result = process_single_word(tokens, False, True, False)
        self.assertEqual(expected, result)

    def test_4_char_long_word_capitalized(self):
        source = "anyw"
        expected = "Anyw"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_3_char_long_word_is_not_capitalized(self):
        source = "the"
        expected = "the"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_noun_is_capitalized(self):
        """
        http://www.yougowords.com/speech/noun/3-letters
        """
        source = "day"
        expected = "Day"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_verb_is_capitalized(self):
        """
        http://www.yougowords.com/speech/noun/3-letters
        """
        source = "run"
        expected = "Run"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_pronoun_is_capitalized(self):
        source = "you"
        expected = "You"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_adjective_is_capitalized(self):
        source = "big"
        expected = "Big"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_adverb_is_capitalized(self):
        source = "ago"
        expected = "Ago"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_adverb_is_capitalized(self):
        source = "ago"
        expected = "Ago"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_words_after_hyphen_is_capitalized(self):
        source = "fan-damn-tastic"
        expected = "Fan-Damn-Tastic"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_why(self):
        """
        Because why is WRB
        """
        source = "why"
        expected = "Why"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_capitalize_alpha(self):
        source = capitalize_alpha("'result")
        expected = "'Result"
        tokens = nlp(source)
        result = process_single_word(tokens, False, False, False)
        self.assertEqual(expected, result)

    def test_capitalize_nth(self):
        source = capitalize_alpha("4th")
        expected = "4th"
        tokens = nlp(source)
        result = process_single_word(tokens, True, False, False)
        self.assertEqual(expected, result)
