import itertools
from collections import defaultdict


def equal_dicts(d1, d2, ignore_keys=()):
    d1_filtered = dict((k, v) for k, v in d1.items() if k not in ignore_keys)
    d2_filtered = dict((k, v) for k, v in d2.items() if k not in ignore_keys)
    return d1_filtered == d2_filtered


with open('official-2014.combined-withalt.m2') as f:
    count = 0
    data = dict()
    for line in f:
        line = line.strip()
        if not line:
            continue

        if line[0] == 'S':
            # sentence
            sentence = line[2:]
            sentence_tuple = (count, sentence)
            data[sentence_tuple] = []
        else:
            # annotation
            annotation = line[2:]
            items = annotation.split('|||')
            items_dict = {
                'pos_start': int(items[0].split()[0]),
                'pos_end': int(items[0].split()[1]),
                'error': items[1],
                'correction': items[2],
                'author': int(items[-1])
            }
            data[sentence_tuple].append(items_dict)

        count += 1

error_types = set()
for sent, annotations in data.items():
    for ann in annotations:
        if ann.get('error'):
            error_types.add(ann['error'])

errors_scores = defaultdict(int)
avg_pair_errors_scores_list = list()
pair_avg_scores = dict()
for sentence_tuple, annotations in data.items():
    annotators_ids = [i['author'] for i in annotations]
    if len(annotators_ids) > 1:
        annotators_pairs = list(itertools.combinations(annotators_ids, 2))

        for pair in annotators_pairs:
            if pair[0] == pair[1]:
                continue
            first_fixes = [i for i in annotations if i['author'] == pair[0]]
            second_fixes = [i for i in annotations if i['author'] == pair[1]]
            pair_errors_scores = defaultdict(list)
            avg_pair_errors_scores = defaultdict(float)

            for i in first_fixes:
                corresponding_fix = next((j for j in second_fixes if equal_dicts(i, j, ['author'])), None)

                if corresponding_fix:
                    pair_errors_scores[i['error']].append(1)
                    second_fixes = [f for f in second_fixes if f != corresponding_fix]
                else:
                    almost_corresponding_fix = next((j for j in second_fixes
                                                     if equal_dicts(i, j, ['author', 'error']) or
                                                     equal_dicts(i, j, ['author', 'correction'])), None)
                    if almost_corresponding_fix:
                        pair_errors_scores[i['error']].append(0.5)
                        if i['error'] != almost_corresponding_fix['error']:
                            pair_errors_scores[almost_corresponding_fix['error']].append(0.5)

                        second_fixes = [f for f in second_fixes if f != almost_corresponding_fix]

            for i in second_fixes:

                corresponding_fix = next((j for j in second_fixes if equal_dicts(i, j, ['author'])), None)

                if corresponding_fix:
                    pair_errors_scores[i['error']].append(1)
                    first_fixes = [f for f in first_fixes if f != corresponding_fix]
                else:
                    almost_corresponding_fix = next((j for j in second_fixes
                                                     if equal_dicts(i, j, ['author', 'error']) or
                                                     equal_dicts(i, j, ['author', 'correction'])), None)
                    if almost_corresponding_fix:
                        pair_errors_scores[i['error']].append(0.5)
                        if i['error'] != almost_corresponding_fix['error']:
                            pair_errors_scores[almost_corresponding_fix['error']].append(0.5)

                        first_fixes = [f for f in first_fixes if f != almost_corresponding_fix]

            for error, value in pair_errors_scores.items():
                avg_pair_errors_scores[error] = sum(value) / len(value)
            avg_pair_errors_scores_list.append(avg_pair_errors_scores)
            pair_avg_scores[pair] = sum(avg_pair_errors_scores.values()) / len(avg_pair_errors_scores.keys())


for error in error_types:
    tmp = list()
    for item in avg_pair_errors_scores_list:
        if item.get(error):
            tmp.append(item[error])

    errors_scores[error] = sum(tmp) / len(tmp)

total_scores = sum(pair_avg_scores.values())/len(pair_avg_scores.keys())

with open("annotation_comparisons_results.txt","w") as f:
    f.write(f'Total: {total_scores}\n\n')
    f.write("Pair scores:\n")
    for pair, scores in pair_avg_scores.items():
        f.write(f"{pair}: {scores}\n")
    f.write("\n")
    f.write("Error scores:\n")
    for error, scores in errors_scores.items():
        f.write(f"{error}: {scores}\n")
