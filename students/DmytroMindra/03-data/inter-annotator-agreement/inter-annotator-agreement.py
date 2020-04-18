#
#   An algorithm to calculate the annotator agreement metric on NUCLE Error Corpus
#
import os
from nltk import agreement
from scipy import spatial

file_path = os.getcwd() + '/../data/official-2014.combined-withalt.m2'

POSITIVE_VALUE = 1
NEGATIVE_VALUE = 0


class Score:
    def __init__(self, score):
        self.score = score
        self.count = 0


class Correction:
    def __init__(self, span_start, span_end, error_type, corrections):
        self.spanStart = span_start
        self.spanEnd = span_end
        self.corrections = corrections
        self.errorType = error_type

    def __eq__(self, other):
        return self.spanStart == other.spanStart and \
               self.spanEnd == other.spanEnd and \
               self.errorType == other.errorType and \
               self.corrections == other.corrections

    def __hash__(self):
        return hash((self.spanStart, self.spanEnd, self.corrections, self.errorType))


class Sentence:
    def __init__(self, text):
        self.text = text
        self.annotations = []


class Annotation:
    def __init__(self, correction, annotator):
        self.annotator = annotator
        self.correction = correction


def read_annotations():
    file = open(file_path)
    lines = file.readlines()
    sentenses = []
    current_sentence = None

    for line in lines:

        if line.startswith("S"):
            sentence = Sentence(line[2:].strip())
            sentenses.append(sentence)
            current_sentence = sentence

        if line.startswith("A"):
            fields = line[2:].strip().split("|||")
            spans = fields[0].split()
            annotation = Annotation(Correction(spans[0], spans[1], fields[1], fields[2]), fields[5])
            current_sentence.annotations.append(annotation)

    return sentenses


def precalculate_sentence_data(by_annotator, by_span, distinct_corrections, distinct_types, sentence):
    for annotation in sentence.annotations:
        span = annotation.correction.spanStart
        annotator = annotation.annotator
        if span not in by_span:
            by_span.update({span: []})
        by_span[span].append(annotation)

        if annotator not in by_annotator:
            by_annotator.update({annotator: []})

        by_annotator[annotator].append(annotation.correction)

        if annotation.correction not in distinct_corrections:
            distinct_corrections.update({annotation.correction: []})

        if annotation.correction.errorType not in distinct_types:
            correction_type = annotation.correction.errorType
            distinct_types.update({correction_type: []})

        distinct_types[annotation.correction.errorType].append(annotation.correction)


# returns vectors of 1 and 0.
# distinct corrections are in columns and annotators are in rows
# if an annotator made a correction similar to one in column, the cell is marked with 1

def get_vectors_for_all_corrections(by_annotator, distinct_corrections):
    vectors = []
    for annotator in by_annotator:
        vector = []
        for correction in distinct_corrections:
            if correction in by_annotator[annotator]:
                vector.append(POSITIVE_VALUE)
            else:
                vector.append(NEGATIVE_VALUE)
        vectors.append(vector)
    return vectors


def calculate_similarity(vectors):
    rows = len(vectors)
    columns = len(vectors[0])

    total_score = 0
    for column in range(columns):
        column_sum = 0
        for row in range(rows):
            column_sum += vectors[row][column]
        total_score += (column_sum-POSITIVE_VALUE)/rows
    return total_score/columns

def calculate_scores(sentences):

    score_by_type = {}
    annotated_count = 0
    inter_annotator_agreement = 0

    for sentence in sentences:
        by_span = {}
        by_annotator = {}
        distinct_corrections = {}
        distinct_types = {}
        vectors_by_error_type = {}


        # finding annotations by span start would be easier for comparison
        precalculate_sentence_data(by_annotator, by_span, distinct_corrections, distinct_types, sentence)
        vectors = get_vectors_for_all_corrections(by_annotator, distinct_corrections)
        get_vectors_by_error_type(by_annotator, vectors_by_error_type, distinct_types, score_by_type)

        # print(vectors_by_error_type)
        # print(sentence.text)

        # for vector in vectors:
        #    print(vector)

        num_annotators = len(by_annotator)
        num_corrections = len(distinct_corrections)


        if (num_annotators > 1):
            annotated_count += 1
            for dtype in distinct_types:
                local_agreement_by_type =calculate_similarity(vectors_by_error_type[dtype])
                score_by_type[dtype].score += local_agreement_by_type
                score_by_type[dtype].count += 1
                #print(dtype, similarity)

        local_agreement = calculate_similarity(vectors)
        inter_annotator_agreement += local_agreement
        #print(local_agreement)

    print('**Average agreement score:**', '{:.4f}'.format(inter_annotator_agreement/annotated_count))
    print('**Agreement by error category:**')
    for error_type in score_by_type:
        print('{}: {:.4f}\\'.format(error_type,score_by_type[error_type].score/score_by_type[error_type].count))

def get_vectors_by_error_type(by_annotator, by_type_vectors, distinct_types, score_by_type):
    for dtype in distinct_types:
        for annotator in by_annotator:
            vector = []
            for correction in distinct_types[dtype]:
                if correction in by_annotator[annotator]:
                    vector.append(POSITIVE_VALUE)
                else:
                    vector.append(NEGATIVE_VALUE)
            if dtype not in by_type_vectors:
                by_type_vectors.update({dtype: []})

            if dtype not in score_by_type:
                score_by_type.update({dtype: Score(0)})
            by_type_vectors[dtype].append(vector)


if __name__ == "__main__":
    # execute only if run as a script

    sentences = read_annotations()
    scores = calculate_scores([sentense for sentense in sentences if len(sentense.annotations) > 0])
