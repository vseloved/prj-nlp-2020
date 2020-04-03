
import logging
import logging.config
import itertools
import time
import datetime as dt
import sys
import io
import bz2

import ruamel.yaml
import coloredlogs

log = logging.getLogger(__name__)


def identity(x):
    return x


def take(n, iterable):
    return itertools.islice(iterable, n)


def format_number(n):
    return '{n:,d}'.format(n=n).replace(',', ' ')


def log_iterator_progress(name, n, iterable, log=log):
    prefix = f'[{name}]'
    log.debug(f'{prefix} ... starting ...')
    beg = time.monotonic()
    i = 0
    for obj in iterable:
        yield obj
        i += 1
        if i % n == 0:
            current = time.monotonic()
            elapsed = dt.timedelta(seconds=(current - beg))
            ii = format_number(i)
            log.debug(f'{prefix} ... processed: {ii}, elapsed: {elapsed}')
    end = time.monotonic()
    elapsed = dt.timedelta(seconds=(end - beg))
    ii = format_number(i)
    log.debug(f'{prefix} ... finished: {ii}, time: {elapsed}')


class ColoredFormatter(coloredlogs.ColoredFormatter):

    def formatTime(self, record, datefmt=None):
        return logging.Formatter.formatTime(self, record, datefmt)


def custom_global_logging_setup():
    logging.TRACE = logging.DEBUG - 1
    logging.addLevelName(logging.TRACE, 'TRACE')

    def log_trace(self, message, *args, **kws):
        if self.isEnabledFor(logging.TRACE):
            self._log(logging.TRACE, message, args, **kws)

    logging.Logger.trace = log_trace

    iso8601fmt = '%Y-%m-%dT%H:%M:%S'
    logging.Formatter.converter = time.gmtime  # use UTC timezone in logs
    logging.Formatter.default_time_format = iso8601fmt
    logging.Formatter.default_msec_format = '%s.%03d'

    coloredlogs.DEFAULT_LEVEL_STYLES['trace'] = dict(color='blue')


def setup_logging_for_debug():
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)-8s %(message)s",
        level=logging.DEBUG,
        stream=sys.stderr,
    )


def setup_logging(logconfig_filename):
    yaml = ruamel.yaml.YAML()
    with io.open(logconfig_filename, 'rt', encoding='utf-8') as text_istream:
        config = yaml.load(text_istream)
    logging.config.dictConfig(config)


def make_chunks_from_stream(chunk_size, binary_istream):
    while True:
        chunk = binary_istream.read(chunk_size)
        if len(chunk) == 0:
            break
        yield chunk


def bz2_decompress_chunks(bz2_chunks):
    decompressor = bz2.BZ2Decompressor()
    for bz2_chunk in bz2_chunks:
        yield decompressor.decompress(bz2_chunk)
        while not decompressor.needs_input and not decompressor.eof:
            yield decompressor.decompress(b'')


class BytesStreamFromChunks(io.RawIOBase):

    def __init__(self, chunks):
        self.chunks_iterator = iter(chunks)
        self.buffer = bytearray()

    def read(self, size=-1):

        if size == -1:
            result = self.buffer
            self.buffer = bytearray()
            for chunk in self.chunks_iterator:
                result += chunk
            return result

        result = bytearray()

        assert size >= 0
        result += self.buffer[:size]
        del self.buffer[:len(result)]
        if len(result) == size:
            return result

        assert len(self.buffer) == 0
        for chunk in self.chunks_iterator:
            result += chunk
            if len(result) > size:
                break
        self.buffer = result[size:]
        del result[size:]

        return result


def make_stream_from_chunks(chunks_iterator):
    stream = BytesStreamFromChunks(chunks_iterator)
    return stream


def arithmetic_mean(a):
    return sum(a) / len(a)


def harmonic_mean(a, b):
    assert a >= 0 and b >= 0
    if a == 0 or b == 0:
        return 0
    return 2 * a * b / (a + b)


def median(a):
    assert a
    if len(a) == 1:
        return a[0]
    a = sorted(a)
    m, r = divmod(len(a), 2)
    if r == 1:
        return a[m]
    return arithmetic_mean((a[m], a[m + 1]))


def f1_score(na, nb, nab):
    assert nab >= 0
    assert na >= nab and nb >= nab
    pab, pba = 0, 0
    if na != 0:
        pba = nab / na
    if nb != 0:
        pab = nab / nb
    return harmonic_mean(pab, pba)
