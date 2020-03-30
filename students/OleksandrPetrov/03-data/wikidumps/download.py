#!/usr/bin/env python

import os
import io
import hashlib
import subprocess
import sys

HERE = os.path.abspath(os.path.dirname(__file__))

AWS_S3_URI_PREFIX = 's3://nlp2020-avp/wikidumps/'


def read_filelist():
    filepath = os.path.join(HERE, 'checksums.sha1')
    with io.open(filepath, 'rt', encoding='utf-8') as text_istream:
        for line in text_istream:
            checksum, filename = line.strip().split(maxsplit=1)
            yield (checksum, filename)


def make_chunks_from_stream(chunk_size, binary_istream):
    while True:
        chunk = binary_istream.read(chunk_size)
        if len(chunk) == 0:
            break
        yield chunk


def sha1_hash(filename):
    Mb = 10**6
    sha1 = hashlib.sha1()
    filepath = os.path.join(HERE, filename)
    try:
        with io.open(filepath, 'rb') as binary_istream:
            chunks = make_chunks_from_stream(10 * Mb, binary_istream)
            for chunk in chunks:
                sha1.update(chunk)
    except FileNotFoundError:
        return None
    else:
        return sha1.hexdigest()


def download_file(filename):
    args = ('aws', 's3', 'cp', AWS_S3_URI_PREFIX + filename, HERE)
    job = subprocess.run(args)
    job.check_returncode()


def main():
    for checksum, filename in read_filelist():
        if sha1_hash(filename) == checksum:
            continue
        download_file(filename)
        if sha1_hash(filename) != checksum:
            print('checking hash failed: {}'.format(filename), file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
