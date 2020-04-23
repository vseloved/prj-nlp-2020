import os

absDir = os.path.dirname(os.path.abspath(__file__))
data_file_name = './official-2014.combined-withalt.m2.txt'
data_file = os.path.join(absDir, data_file_name)

with open(data_file) as f:
    corpus = f.read()


def parse_annotation(text):
    parts = text.replace('A ', '').split('|||')
    nums = parts[0].split(' ')
    return {
        'start': int(nums[0]),
        'end': int(nums[1]),
        'err_tag': parts[1],
        'replacement': parts[2],
        'ann_num': parts[5]
    }


def get_pairs(lst):
    return list(zip(lst, lst[1:]))


def get_annotation_blocks(corpus):
    blocks = corpus.split('\n\n')
    res = {}
    for block in blocks:
        group = block.split('\n')

        # skip sentences with one or zero annotations
        if len(group) < 3:
            continue
        sent = group[0].replace('S ', '')
        res[sent] = {}
        for annot in group[1:]:
            if annot:
                parsed = parse_annotation(annot)
                if not res[sent].get(parsed['ann_num']):
                    res[sent][parsed['ann_num']] = []
                res[sent][parsed['ann_num']].append(parsed)

    return {sent: anns for sent, anns in res.items()}


def find_correction(lst, predicate):
    corrs_filtered = [x for x in lst if predicate(x)]
    return corrs_filtered[0] if corrs_filtered else None


def compare_annotator_pair(fst, snd):
    matches_gen = 0
    matches_by_err_tag = {}

    for f in fst:
        f_start = f['start']
        f_end = f['end']
        f_repl = f['replacement']
        err_tag = f['err_tag']
        is_noop = err_tag == 'noop'

        for s in snd:
            s_start = s['start']
            s_end = s['end']
            s_repl = s['replacement']
            is_start_match = f_start == s_start
            is_end_match = f_end == s_end

            is_match = False

            if is_start_match and is_end_match:
                is_match = f_repl == s_repl

            """
            Quite a naive an unoptimized logic
            for finding intersecting annotations:

            - if one of the boundary matches - look for another correction in the list
            with a shorter range, and concat its replacement value to the currect value
            - if the contatenated value equals to the one we compare with -
            we may assume that those two corrections actually mean the same
            """
            if is_start_match and not is_end_match:
                if s_end > f_end:
                    next_corr = find_correction(
                        fst, lambda x: x['end'] == s_end)
                    if next_corr:
                        next_repl = next_corr['replacement']
                        is_match = f_repl + next_repl == s_repl
                else:
                    next_corr = find_correction(
                        snd, lambda x: x['end'] == f_end)
                    if next_corr:
                        next_repl = next_corr['replacement']
                        is_match = f_repl + next_repl == s_repl
            if not is_start_match and is_end_match:
                if f_start > s_start:
                    prev_corr = find_correction(
                        fst, lambda x: x['start'] == s_start)
                    if prev_corr:
                        prev_repl = prev_corr['replacement']
                        is_match = prev_repl + f_repl == s_repl
                else:
                    prev_corr = find_correction(
                        snd, lambda x: x['start'] == f_start)
                    if prev_corr:
                        prev_repl = prev_corr['replacement']
                        is_match = prev_repl + f_repl == s_repl

            if is_match:
                matches_gen += 1

            if is_match and err_tag == s['err_tag'] and not is_noop:
                if matches_by_err_tag.get(err_tag):
                    matches_by_err_tag[err_tag] += 1
                else:
                    matches_by_err_tag[err_tag] = 1
            else:
                if not matches_by_err_tag.get(err_tag) and not is_noop:
                    matches_by_err_tag[err_tag] = 0

    return matches_gen, matches_by_err_tag


def get_pair_agreement(fst, snd):
    matches_gen, matches_by_err_type = compare_annotator_pair(fst, snd)

    # Get unique corrections to not count matches twice
    distinct_corrections = len(fst) + len(snd) - matches_gen
    agr_gen = round(matches_gen/distinct_corrections, 2)
    return agr_gen, matches_by_err_type


def get_inter_ann_agr_pair(sentence, annotations, existing_pair_agrs):
    pairwise_list = get_pairs(list(annotations.values()))

    # In order to not mutate function arg
    new_pair_agrs = existing_pair_agrs.copy()

    for fst, snd in pairwise_list:
        pair_num = int(fst[0]['ann_num'])
        pair_agr_gen, pair_agr_err_type = get_pair_agreement(fst, snd)
        new_pair_agrs[pair_num].append((pair_agr_gen, pair_agr_err_type))
    return new_pair_agrs


def get_all_inter_ann_agr(corpus):
    annotation_blocks = get_annotation_blocks(corpus)
    pair_agrs = [[] for _ in range(0, 4)]  # 4 possible pairs of 5 annonators

    for sent, ann in annotation_blocks.items():
        # skip sentences with a single annotator
        if len(ann.keys()) > 1:
            pair_agrs = get_inter_ann_agr_pair(sent, ann, pair_agrs)

    pair_agrs_gen = [[x for x, _ in y] for y in pair_agrs]
    agr_by_annot_pairs = [sum(x)/len(x) for x in pair_agrs_gen if x]

    # General mean
    avg_agr_by_annottators = round(sum(agr_by_annot_pairs)/4, 2)

    pair_agrs_by_err = [[x for _, x in y if x] for y in pair_agrs]
    pair_agrs_by_err_flattened = [
        x for sublist in pair_agrs_by_err for x in sublist]

    # Mean by error types
    avg_agr_by_err_type = {}

    # Group all errot tag means by error types
    for x in pair_agrs_by_err_flattened:
        for k, v in x.items():
            if avg_agr_by_err_type.get(k):
                prev = avg_agr_by_err_type[k]
                # average between previous and current mean
                avg_agr_by_err_type[k] = (v + prev)/2
            else:
                avg_agr_by_err_type[k] = v
    for k, v in avg_agr_by_err_type.items():
        # Multiply by the generic mean since it should be reltive to it
        avg_agr_by_err_type[k] = round(v * avg_agr_by_annottators, 2)

    return avg_agr_by_annottators, avg_agr_by_err_type


all_inter_ann_agr = get_all_inter_ann_agr(corpus)
print(all_inter_ann_agr)
