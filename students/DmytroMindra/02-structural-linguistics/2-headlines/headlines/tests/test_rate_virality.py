import unittest

from headlines.virality.rate_header_virality import parse_document, contains_named_entity, \
    contains_comparative_or_superlative, sentence_score


class ViralityTestCases(unittest.TestCase):

    def test_named_entity_present(self):
        source = "Lil Wayne Is Contemplating Life as a Married Man."
        document = parse_document(source)
        result = contains_named_entity(document)
        self.assertEqual(True, result)


    def test_named_entity_absent(self):
        source = "We have tried to write a book that assists students in discovering the power of programming."
        document = parse_document(source)
        result = contains_named_entity(document)
        self.assertEqual(False, result)

    def test_named_contains_comparative_or_superlative(self):
        sources = [
            "Mark is fast but Bob is faster.",
            "Jack is the fastest runner in our team.",
            "He drives fast, but we can drive faster than him.",
            "We drive the fastest we can."
        ]
        for source in sources:
            document = parse_document(source)
            result = contains_comparative_or_superlative(document)
            self.assertEqual(True, result)


    def test_positive_sentence_score(self):
        source = "This is a shiny positive sentence."
        document = parse_document(source)
        score = sentence_score(source, document, threshold=0.75)[0]
        self.assertGreater(score,0)

    def test_negqtive_sentence_score(self):
        source = "This is an ugly negative sentence."
        document = parse_document(source)

        score = sentence_score(source, document, threshold=0.75)[0]
        self.assertLess(score,0)

