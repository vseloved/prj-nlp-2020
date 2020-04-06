import re
from tqdm import tqdm
from students.BohdanYatsyna.homework3.annotation import Annotation
from students.BohdanYatsyna.homework3.annotation import annotationType
from students.BohdanYatsyna.homework3.annotation import AnnotatedSentence


def ann_aggeed_check(senences, agreed_type=''):
    annot_count = 0
    annot_agreed = 0

    for sent in senences:
        for i, annotator in enumerate(sent.annotations):
            if agreed_type:
                if agreed_type == annotator.type:
                    annot_count += 1
            else:
                annot_count += 1
            for j, ann in enumerate(sent.annotations):
                if j == i:
                    continue
                elif ann == annotator:
                    if agreed_type:
                        if agreed_type == annotator.type:
                            annot_agreed += 1
                    else:
                        annot_agreed += 1
    if not annot_count: return 0

    return annot_agreed / annot_count


file_path = './official-2014.combined-withalt.m2'
num_lines = sum(1 for line in open(file_path, 'r'))

regEx = {}
# regulars for sentense
regEx['is sent'] = re.compile('^S')
regEx['sent extraction'] = re.compile('(?<=^S ).{1,}')
# regulars for anotators
regEx['is annot'] = re.compile('^A')

is_anotation = False
annotated_sentences = []
count = 0
current_sent = ''

print("Data parsing")
with open(file_path) as file:
    for line in tqdm(file, total=num_lines):
        # sentense
        if regEx['is sent'].match(line):
            is_anotation = True
            count += 1
            current_sent = AnnotatedSentence(regEx['sent extraction'].findall(line))
            current_sent.sentenceNumber = count

        # annotation
        elif is_anotation and regEx['is annot'].match(line):
            annot = Annotation(line)
            current_sent.annotations.append(annot)

        # annotation end
        if line == '\n':
            if current_sent != '':
                annotated_sentences.append(current_sent)
            is_anotation = False
            current_sent = ''

print("Clean data")
cleared_sentences = []
for annotated_sentence in annotated_sentences:
    if len(annotated_sentence.annotations) > 1: cleared_sentences.append(annotated_sentence)

print("Annotation agreed lvl: {}".format(ann_aggeed_check(cleared_sentences)))

for key in annotationType.keys():
    print("Annotation agreed for '{}' lvl: {}".format(key, ann_aggeed_check(cleared_sentences, key)))
