import difflib
import json
import os
import sys
import click

from headlines.formatting.formatting import process_headline
from headlines.virality.rate_header_virality import parse_document, contains_named_entity, sentence_score, \
    contains_comparative_or_superlative

package_directory = os.path.dirname(os.path.abspath(__file__))
path_to_data = package_directory + "/../../../../../tasks/02-structural-linguistics/data/"


def ascii_cat(output_file):
    print("", file=output_file)
    print("   _._     _,-'""`-._", file=output_file)
    print("  (,-.`._,'(       |\`-/|", file=output_file)
    print("      `-.-' \ )-`( , o o)", file=output_file)
    print("            `-    \`_`\"'-", file=output_file)


def execute_evalset():
    with open(path_to_data + 'headlines-test-set.json') as json_file:
        data = json.load(json_file)

    passed_cases = 0
    failed_cases = 0

    file = open("evalset-output.txt", "w+")

    for row in data:
        source = row[0]
        expected = row[1]
        result = process_headline(source)
        if result != expected:
            failed_cases += 1
            print("Failed case #", failed_cases, file=file)
            for line in difflib.ndiff([result], [expected]):
                print(line, file=file)
        else:
            passed_cases += 1

    total_cases = passed_cases + failed_cases

    file.write('Passed : {}\n'.format(passed_cases))
    file.write('Failed : {}\n'.format(failed_cases))
    file.write('total : {}\n'.format(total_cases))
    file.write("Total score on evalset {}/{} = {:.3f}%\n".format(passed_cases, total_cases,
                                                                 passed_cases / total_cases))

    print('Passed : {}'.format(passed_cases))
    print('Failed : {}'.format(failed_cases))
    print('total : {}'.format(total_cases))
    print("Total score on evalset {}/{} = {:.3f}%".format(passed_cases, total_cases,
                                                          passed_cases / total_cases))

    print('See detailed results in evalset-output.txt')
    file.close()


def execute_corpus():
    with open(path_to_data + 'examiner-headlines.txt') as text_file:
        data = text_file.readlines()

    passed_cases = 0
    failed_cases = 0

    file = open("examiner-headlines-output.txt", "w+")

    for line in data:
        source = line
        expected = process_headline(source)
        if source != expected:
            failed_cases += 1
            file.write("Failed case #{}\n".format(failed_cases))
            for line in difflib.ndiff([source], [expected]):
                file.write(line)
            file.write('\n')
        else:
            passed_cases += 1

    total_cases = passed_cases + failed_cases
    file.write('Passed : {}\n'.format(passed_cases))
    file.write('Failed : {}\n'.format(failed_cases))
    file.write('total : {}\n'.format(total_cases))
    file.write("Total score on examiner-headlines corpus {}/{} = {:.2f}%\n".format(passed_cases, total_cases,
                                                                                   passed_cases / total_cases))
    file.close()

    print('Passed : {}'.format(passed_cases))
    print('Failed : {}'.format(failed_cases))
    print('total : {}'.format(total_cases))
    print("Total score on examiner-headlines corpus {}/{} = {:.2f}%".format(passed_cases, total_cases,
                                                                            passed_cases / total_cases))
    print('See detailed results in examiner-headlines-output.txt')

def execute_virality():
    with open(path_to_data + 'examiner-headlines.txt') as text_file:
        data = text_file.readlines()

    has_names_entities = 0
    is_positive = 0
    is_negative = 0
    has_comparative_or_superlative = 0

    file = open("examiner-headlines-output.txt", "w+")

    for line in data:
        source = line
        document = parse_document(source)
        if contains_named_entity(document):
            has_names_entities += 1
        if contains_comparative_or_superlative(document):
            has_comparative_or_superlative += 1
        score = sentence_score(source, document, threshold=0.75)[0]

        if score > 0:
            is_positive += 1

        if score < 0:
            is_negative += 1

    total_headlines = len(data)

    has_names_entities_percent = has_names_entities/total_headlines*100
    is_positive_percent = is_positive/total_headlines*100
    is_negative_percent = is_negative/total_headlines*100
    has_comparative_or_superlative_percent = has_comparative_or_superlative/total_headlines*100

    print('Contains named entity (person/organisation): {:.2f}%'.format(has_names_entities_percent))
    print('Has positive scent: {:.2f}%'.format(is_positive_percent))
    print('Has negative scent: {:.2f}%'.format(is_negative_percent))
    print("Contains comparative or superlative: {:.2f}%".format(has_comparative_or_superlative_percent))
    print('Total headlines: {:.2f}'.format(total_headlines))