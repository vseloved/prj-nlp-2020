
import itertools
import collections


IDENTITY_CORRECTION_TYPE = 'noop'

Region = collections.namedtuple(
    'Region',
    (
        'beg',
        'end',
    )
)

Edit = collections.namedtuple(
    'Edit',
    (
        'region',
        'tokens',
        'type',
    )
)


def make_coverage(n, regions):
    coverage = [0] * n
    for r in regions:
        for i in range(r.beg, r.end):
            coverage[i] += 1
    return coverage


def generate_uncovered_regions(coverage):

    for is_covered, region_it in itertools.groupby(
        enumerate(coverage),
        key=lambda x: x[1] != 0,
    ):
        if is_covered:
            continue
        beg = None
        end = None
        for i, __ in region_it:
            if beg is None:
                beg = i
            end = i
        assert beg is not None and end is not None
        yield Region(beg, end + 1)


def parse_sentence_def(line):
    assert line.startswith('S ')
    line = line[2:]
    tokens = line.split()
    assert tokens
    assert all(map(bool, tokens))
    return tokens


def parse_annotation_def(sentence, line):

    assert line.startswith('A ')
    line = line[2:]
    tokens = [t.strip() for t in line.split('|||')]
    assert all('|' not in t for t in tokens), 'Unexpected format: {}'.format(tokens)
    tokens = [t if t != '-NONE-' else None for t in tokens]

    region_def, edit_type, text, __, __, annotator_id = tokens

    annotator_id = int(annotator_id)

    beg, end = map(int, region_def.split())
    if edit_type == IDENTITY_CORRECTION_TYPE:
        assert beg == -1 and end == -1
        beg, end = (0, len(sentence))
    assert 0 <= beg and beg <= len(sentence)
    assert 0 <= end and end <= len(sentence)
    assert beg <= end

    edit_tokens = text.split() if text is not None else tuple()
    edit_tokens = tuple(edit_tokens)

    return annotator_id, Edit(Region(beg, end), edit_tokens, edit_type)


def parse_sentence_annotation_block(lines):

    lines_it = iter(lines)
    first_line = next(lines_it)
    other_lines = lines_it

    sentence = parse_sentence_def(first_line)

    edits = {}
    for line in other_lines:
        annotator_id, edit = parse_annotation_def(sentence, line)
        if annotator_id not in edits:
            edits[annotator_id] = []
        edits[annotator_id].append(edit)

    # expectation: regions of edits should not overlap
    for __, annotator_edits in edits.items():
        coverage = make_coverage(len(sentence), (e.region for e in annotator_edits))
        assert all(c <= 1 for c in coverage), 'Regions overlap in: {}'.format(annotator_edits)

    return sentence, edits


def iterate_non_empty_blocks_of_lines(lines):
    for is_not_empty, group_it in itertools.groupby(lines, key=bool):
        if is_not_empty:
            yield group_it


def parse(lines):
    lines = map(lambda line: line.strip(), lines)
    blocks = iterate_non_empty_blocks_of_lines(lines)
    sentence_annotations = map(parse_sentence_annotation_block, blocks)
    return sentence_annotations
