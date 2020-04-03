#!/usr/bin/env python

import logging
import io
import pathlib
import bz2
import xml.sax
import time
import datetime as dt
import collections
import multiprocessing
import functools
import itertools
import json

import wikitextparser
import pycld2

import utils

log = logging.getLogger('wiktionary')

THIS_FILE = pathlib.Path(__file__)
THIS_DIR = THIS_FILE.parent
DATA_DIR = THIS_DIR.joinpath('wikidumps')
OUT_DIR = THIS_DIR.joinpath('output')

Mb = 10**6


def lang_reliably_not_equal(lang, text):
    is_reliable, __, details = pycld2.detect(text)
    if is_reliable and details[0][1] != lang:
        return True
    return False


def is_page_useful_for_synonyms(page):
    if page.get('format') != 'text/x-wiki':
        return False
    if page.get('model') != 'wikitext':
        return False
    title = page.get('title')
    if not title:
        return False
    if ':' in title:
        return False
    return True


Page = collections.namedtuple(
    'Page',
    (
        'ns',
        'title',
        'text',
    ),
)


def make_page(page_data):
    return Page._make(page_data.get(k) for k in Page._fields)


def no_filter(page_data):
    return True


class ParseAborted(Exception):
    pass


class WiktionaryContentHandler(xml.sax.ContentHandler):

    PAGE_DATA_TAGS = (
        'ns',
        'title',
        'format',
        'model',
        'text',
    )

    def __init__(self, pages_queue_appender, page_filter=no_filter, page_constructor=utils.identity, pages_limit=None):
        self.pages_limit = pages_limit
        self.pages_parsed = 0
        self.namespaces = {}
        self.tags = []
        self.attrs = []
        self.content_buffer = []
        self.is_page_context = False
        self.is_revision_context = False
        self.page_data = {}
        self.pages_queue_appender = pages_queue_appender
        self.is_page_interesting = page_filter
        self.make_page = page_constructor

    def stop_processing(self):
        self.pages_queue_appender(None)

    def process_page_context_element(self, tag, attrs, data):
        if tag != 'text':
            data = data.strip()
        if (not self.is_revision_context and tag == 'id') or tag in self.PAGE_DATA_TAGS:
            self.page_data[tag] = data
        if tag == 'page':
            if self.is_page_interesting(self.page_data):
                page = self.make_page(self.page_data)
                # log.trace('page: %s', page)
                self.pages_queue_appender(page)
            self.page_data = {}

    def startElement(self, name, attrs):
        self.tags.append(name)
        self.attrs.append(attrs)
        if name == 'page':
            self.is_page_context = True
        elif name == 'revision':
            self.is_revision_context = True

    def endElement(self, name):
        assert name == self.tags[-1]
        data = ''.join(self.content_buffer)
        self.content_buffer = []
        attrs = self.attrs.pop()
        tag = self.tags.pop()
        if self.is_page_context:
            self.process_page_context_element(tag, attrs, data)
        if tag == 'namespace':
            self.namespaces[attrs.get('key')] = data.strip()
        elif tag == 'revision':
            self.is_revision_context = False
        elif tag == 'page':
            self.pages_parsed += 1
            self.is_page_context = False
        if self.pages_limit is not None and self.pages_parsed >= self.pages_limit:
            raise ParseAborted('page limit reached')

    def characters(self, content):
        self.content_buffer.append(content)


class LogErrorHandler(xml.sax.ErrorHandler):

    def __init__(self, log=log):
        self.log = log

    def error(self, e):
        self.log.error(e)

    def fatalError(self, e):
        self.log.critical(e)

    def warning(self, e):
        self.log.warning(e)


def parse_wiktionary_archive(wk_content_handler, filepath, log=log):

    log = log.getChild('xmlparse')

    with io.open(filepath, 'rb') as binary_istream:
        xml_istream = bz2.BZ2File(binary_istream)

        chunks = utils.make_chunks_from_stream(1 * Mb, xml_istream)
        # chunks = utils.take(100, chunks)
        chunks = utils.log_iterator_progress('xml megabytes', 100, chunks, log=log)
        xml_istream = utils.make_stream_from_chunks(chunks)

        error_handler = LogErrorHandler(log=log)
        try:
            xml.sax.parse(xml_istream, wk_content_handler, error_handler)
        except ParseAborted as e:
            log.warning('xml parsing stopped: %s', e)

        wk_content_handler.stop_processing()


def extract_synonyms_de(page):

    def iterate_synonym_blocks(page):
        r = wikitextparser.parse(page.text)
        for n, t in enumerate(r.templates):
            if 'Synonyme' not in t.name:
                continue
            beg = t.span[1]
            end = r.templates[n + 1].span[0] if n + 1 < len(r.templates) else r.span[1]
            syn_block = r(beg, end)
            yield syn_block

    def parse_synonym_block(text):
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            r = wikitextparser.parse(line)
            syn_group = tuple(wl.title for wl in r.wikilinks)
            if syn_group:
                yield syn_group

    # log.warning('page: %s', page.title)

    lang_reliably_not_equal_de = functools.partial(lang_reliably_not_equal, 'de')

    word = page.title

    if lang_reliably_not_equal_de(word):
        return []

    synonym_rows = []
    for sb in iterate_synonym_blocks(page):
        for synonym_group in parse_synonym_block(sb):
            txt_for_test = '{} {}'.format(word, ' '.join(synonym_group))
            if lang_reliably_not_equal_de(txt_for_test):
                continue
            # log.debug('sg: %s', synonym_group)
            synonym_rows.append((word, synonym_group))

    return synonym_rows


# def extract_synonyms_ru(page):
#     log.warning('page: %s', page)
#     r = wikitextparser.parse(page.text)
#     for s in r.sections:
#         # if 'Синоним' not in s.title and 'Значен' not in s.title:
#         #     continue
#         log.debug('section: %s \n%s', s.title, s.contents)
#     # for t in r.templates:
#     #     log.debug('template: %s', t.name)
#     return []


SYNONYMS_EXTRACTORS = {
    'de': extract_synonyms_de,
    # 'ru': extract_synonyms_ru,
}


def process_wiktionary_arhive(filepath):

    log.info('input: %s', filepath)

    lang = filepath.name[:2]

    if lang not in SYNONYMS_EXTRACTORS:
        log.warning('language [%s] not supported, file skipped', lang)
        return

    extract_synonyms = SYNONYMS_EXTRACTORS[lang]

    # pages = []

    # handler = WiktionaryContentHandler(
    #     pages.append,
    #     page_filter=is_page_useful_for_synonyms,
    #     page_constructor=make_page,
    #     # pages_limit=500,
    # )

    # parse_wiktionary_archive(handler, filepath, log=log)

    pages_queue = multiprocessing.Queue(10**4)

    handler = WiktionaryContentHandler(
        pages_queue.put,
        page_filter=is_page_useful_for_synonyms,
        page_constructor=make_page,
        # pages_limit=500,
    )

    parse_job = functools.partial(parse_wiktionary_archive, handler, filepath, log=log)

    parse_process = multiprocessing.Process(name='xmlparser', target=parse_job)
    parse_process.start()

    def iterate_queue(q, stop_predicate):
        minute = 60.0
        read_timeout = 1 * minute
        while True:
            obj = q.get(block=True, timeout=read_timeout)
            if stop_predicate(obj):
                break
            yield obj

    def process_in_parallel(fn, iterable):
        n_workers = max(multiprocessing.cpu_count() - 1, 1)
        chunksize = 10**3
        log.debug('starting to process with %s worker(s) ...', n_workers)
        with multiprocessing.Pool(processes=n_workers) as pool:
            for result in pool.imap_unordered(fn, iterable, chunksize):
                yield result

    pages = iterate_queue(pages_queue, lambda page: page is None)
    pages = utils.log_iterator_progress('wiki pages', 5 * 10**4, pages, log=log)

    processor = process_in_parallel
    # processor = map

    results = processor(extract_synonyms, pages)
    synonym_rows = itertools.chain.from_iterable(results)

    synonym_rows = utils.log_iterator_progress('synonym rows', 10**4, synonym_rows, log=log)

    synonym_rows = list(synonym_rows)
    synonym_rows = sorted(synonym_rows, key=lambda r: r[0])

    outfilename = filepath.with_suffix('').with_suffix('.synonyms.jsonl').name
    outfilepath = OUT_DIR.joinpath(outfilename)
    log.info('output: %s', outfilepath)
    with io.open(outfilepath, 'wt', encoding='utf-8') as text_ostream:
        for sr in synonym_rows:
            sr_json = json.dumps(sr, ensure_ascii=False)
            text_ostream.write(sr_json)
            text_ostream.write('\n')

    parse_process.join()


def main():
    utils.custom_global_logging_setup()
    utils.setup_logging(THIS_FILE.with_suffix('.logconfig.yaml'))

    log.info('starting...')

    def is_filepath_interesting(filepath):
        lang = filepath.name[:2]
        return lang == 'de'

    filepaths = DATA_DIR.glob('*.bz2')

    filepaths = filter(is_filepath_interesting, filepaths)
    filepaths = utils.log_iterator_progress('files', 1, filepaths, log=log)

    for filepath in filepaths:
        process_wiktionary_arhive(filepath)

    log.info('finished')


if __name__ == '__main__':
    main()
