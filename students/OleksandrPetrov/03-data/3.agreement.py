#!/usr/bin/env python

import logging
import pathlib
import io
import functools
import itertools

import ruamel.yaml

import utils
import m2format

log = logging.getLogger('agreement')

THIS_FILE = pathlib.Path(__file__)
THIS_DIR = THIS_FILE.parent
DATA_DIR = THIS_DIR.joinpath('conll14st-test-data', 'alt')
OUT_DIR = THIS_DIR.joinpath('output')


def normalize_to_single_token_edits(edit):

    def positions_it(region):
        return itertools.chain(
            (m2format.Region(pos, pos + 1) for pos in range(region.beg, region.end)),
            itertools.repeat(m2format.Region(region.end, region.end)),
        )

    def tokens_it(tokens):
        return itertools.chain(
            ((token,) for token in tokens),
            itertools.repeat(tuple()),
        )

    region = edit.region
    tokens = edit.tokens

    if region.beg == region.end:
        yield edit
        return

    n = max(region.end - region.beg, len(tokens))
    for st_region, st_tokens in utils.take(n, zip(positions_it(region), tokens_it(tokens))):
        assert region.beg <= st_region.beg and st_region.end <= region.end
        yield m2format.Edit(st_region, st_tokens, edit.type)


def make_homogeneous_sentence_annotations(sentence_annotations):

    annotators_ids = set(
        annotator_id
        for __, annotators_sentence_edits in sentence_annotations
        for annotator_id in annotators_sentence_edits.keys()
    )

    sentences = []
    annotations = {annotator_id: [] for annotator_id in annotators_ids}

    for sentence, annotators_sentence_edits in sentence_annotations:
        sentences.append(sentence)
        n = len(sentence)
        for annotator_id, edits in annotations.items():
            if annotator_id not in annotators_sentence_edits:
                annotator_edits = [
                    m2format.Edit(m2format.Region(0, n), tokens=tuple(), type=None)
                ]
            else:
                annotator_edits = annotators_sentence_edits[annotator_id]
                coverage = m2format.make_coverage(n, (e.region for e in annotator_edits))
                explicit_identity_edits = (
                    m2format.Edit(r, tokens=tuple(), type=m2format.IDENTITY_CORRECTION_TYPE)
                    for r in m2format.generate_uncovered_regions(coverage)
                )
                annotator_edits.extend(explicit_identity_edits)
            edits.append(annotator_edits)

    assert set(len(edits) for edits in annotations.values()) == {len(sentences)}
    return sentences, annotations


def concatenate_edits(edits_iterable):
    """Precondition: edits fully cover target sample.
    So, at least: sample lengths == max(edit.region.end)
    """

    offset = 0
    for edits in edits_iterable:
        assert edits
        n = max(e.region.end for e in edits)
        for e in edits:
            r = m2format.Region(e.region.beg + offset, e.region.end + offset)
            yield m2format.Edit(r, e.tokens, e.type)
        offset += n


def main():
    utils.custom_global_logging_setup()
    utils.setup_logging(THIS_FILE.with_suffix('.logconfig.yaml'))

    log.info('starting...')

    datafilepath = DATA_DIR.joinpath('official-2014.combined-withalt.m2')
    log.info('input: %s', datafilepath)
    with io.open(datafilepath, 'rt', encoding='utf-8') as text_istream:
        sentence_annotations = m2format.parse(text_istream)
        sentence_annotations = list(sentence_annotations)

    # sentence_annotations = sentence_annotations[5:6]
    # sentence_annotations = sentence_annotations[9:10]

    ##########################################################################
    # making homogeneous
    ##########################################################################

    sentences, annotations = make_homogeneous_sentence_annotations(sentence_annotations)

    ##########################################################################
    # concatenation
    ##########################################################################

    tokens = list(itertools.chain.from_iterable(sentences))
    annotations = {
        annotator_id: list(
            concatenate_edits(annotator_edits),
        )
        for annotator_id, annotator_edits in annotations.items()
    }
    assert set(max(e.region.end for e in edits) for edits in annotations.values()) == {len(tokens)}

    ##########################################################################
    # normalization to single token edits
    ##########################################################################

    annotations = {
        # stdlib [sorted] doing stable sorts, so, not expect to broke order of token inserts here
        annotator_id: sorted(
            itertools.chain.from_iterable(
                map(normalize_to_single_token_edits, annotator_edits)
            ),
            key=lambda edit: (edit.region.beg, edit.region.end - edit.region.beg),
        )
        for annotator_id, annotator_edits in annotations.items()
    }
    assert set(max(e.region.end for e in edits) for edits in annotations.values()) == {len(tokens)}

    ##########################################################################
    # analysis
    ##########################################################################

    def describe(text=None):

        def decorator(f):
            f.description = text if text is not None else f.__name__
            return f

        return decorator

    @describe()
    def filter_both_annotators_saw_token(edits_a, edits_b):

        def positions_saw(edits):
            return set(e.region.beg for e in edits_a if e.type is not None)

        positions_allowed = positions_saw(edits_a) & positions_saw(edits_b)
        edits_a = [e for e in edits_a if e.region.beg in positions_allowed]
        edits_b = [e for e in edits_b if e.region.beg in positions_allowed]
        return edits_a, edits_b

    @describe()
    def erase_all_edit_types(edits_a, edits_b):
        edits_a = [m2format.Edit(e.region, e.tokens, None) for e in edits_a]
        edits_b = [m2format.Edit(e.region, e.tokens, None) for e in edits_b]
        return edits_a, edits_b

    def filter_by_edit_type(edit_type_predicate, edits_a, edits_b):
        edits_a = [e for e in edits_a if edit_type_predicate(e.type)]
        edits_b = [e for e in edits_b if edit_type_predicate(e.type)]
        return edits_a, edits_b

    def analyze(annotations, pair_edits_transforms=tuple()):
        results = {
            'transforms': [t.description for t in pair_edits_transforms],
            'pairs': {},
            'f1_a_mean': None,
            'f1_median': None,
        }
        f1s = []
        annotators_ids = sorted(annotations.keys())
        for a, b in itertools.combinations(annotators_ids, 2):
            edits_a, edits_b = annotations[a], annotations[b]
            for t in pair_edits_transforms:
                edits_a, edits_b = t(edits_a, edits_b)
            edits_a, edits_b = set(edits_a), set(edits_b)
            edits_ab = edits_a & edits_b
            na, nb, nab = len(edits_a), len(edits_b), len(edits_ab)
            f1_score = utils.f1_score(na, nb, nab)
            f1s.append(f1_score)
            results['pairs'][(a, b)] = [round(f1_score, 4), na, nb, nab]
        results['f1_a_mean'] = round(utils.arithmetic_mean(f1s), 4)
        results['f1_median'] = round(utils.median(f1s), 4)
        return results

    def generate_various_analysis(annotations):

        yield analyze(annotations)
        yield analyze(annotations, (filter_both_annotators_saw_token,))
        yield analyze(annotations, (filter_both_annotators_saw_token, erase_all_edit_types))

        error_types = set(
            e.type
            for edits in annotations.values()
            for e in edits
            if e.type is not None
        )
        error_types = sorted(error_types)

        def make_error_type_filter(edit_type):
            etf = functools.partial(filter_by_edit_type, lambda et: et == edit_type)
            return describe('edit.type == {}'.format(edit_type))(etf)

        error_type_filters = [make_error_type_filter(et) for et in error_types]
        for etf in error_type_filters:
            yield analyze(annotations, (filter_both_annotators_saw_token, etf))

    results = generate_various_analysis(annotations)
    results = utils.log_iterator_progress('analysis', 1, results, log=log)

    outfilename = THIS_FILE.with_suffix('.results.yaml')
    outfilepath = OUT_DIR.joinpath(outfilename)
    log.info('output: %s', outfilepath)
    with io.open(outfilepath, 'wt', encoding='utf-8') as text_ostream:
        yaml = ruamel.yaml.YAML(typ='safe', pure=True)
        yaml.dump_all(results, text_ostream)

    log.info('finished')


if __name__ == '__main__':
    main()
