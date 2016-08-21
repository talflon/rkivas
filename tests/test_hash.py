import hashlib
import os.path
import re
from random import Random
from unittest.mock import Mock, patch

import pytest
import hypothesis.strategies as hs
from hypothesis import given, assume

import rkivas
from rkivas import hash_file, encode_hash, Archiver


@given(hs.lists(hs.binary(max_size=10, min_size=1), max_size=10))
def test_hash_file(read_results):
    class MockFile:
        def __init__(self, data):
            self.data = data[:]
            self.data.reverse()

        def read(self, size=-1):
            if not self.data:
                return b''
            assert size >= len(self.data[-1])
            return self.data.pop(-1)

        def readinto(self, b):
            data = self.read(len(b))
            b[:len(data)] = data
            return len(data)

    class MockDigest:
        def __init__(self):
            self.data = b''

        def update(self, d):
            assert len(d) > 0
            self.data += d

        def digest(self):
            return self.data

    result = hash_file(MockDigest(), MockFile(read_results), buffer_size=10)
    expected = b''.join(read_results)
    assert result == expected


class TestEncodeHash:

    @given(hs.binary(min_size=1, max_size=10),
           hs.integers(min_value=1, max_value=16))
    def test_is_deterministic(self, hashed, length):
        assume(len(hashed) * 8 >= length * 5)
        result = encode_hash(hashed, length)
        assert result == encode_hash(hashed, length)

    @given(hs.binary(min_size=1, max_size=10),
           hs.integers(min_value=1, max_value=16))
    def test_length(self, hashed, length):
        assume(len(hashed) * 8 >= length * 5)
        result = encode_hash(hashed, length)
        assert len(result) == length

    @given(hs.binary(min_size=1, max_size=10),
           hs.integers(min_value=1, max_value=16))
    def test_characters(self, hashed, length):
        assume(len(hashed) * 8 >= length * 5)
        result = encode_hash(hashed, length)
        assert re.match(rb'^[0-9a-z]', result)

    def test_depends_on_input(self):
        rand = Random(98457234)
        hashed = [bytes(rand.randrange(256) for _ in range(10)) for _ in range(5)]
        results = [encode_hash(h, 4) for h in hashed]
        assert len(set(results)) == len(results)


def check_get_hash(algorithm, digest, contents, tmpdir, length=7):
    filename = os.path.join(str(tmpdir), 'file_to_hash')
    with open(filename, 'wb') as f:
        f.write(contents)
    digest.update(contents)
    expected = digest.digest()
    with patch.object(rkivas, 'encode_hash') as mock_encode_hash:
        mock_encode_hash.return_value = b'success'
        result = Archiver({}).get_hash({
            'hash-algorithm': algorithm,
            'hash-length': str(length),
        }, filename)
        mock_encode_hash.assert_called_once_with(expected, length)
        assert result == 'success'


@pytest.mark.parametrize('algorithm', ['md5', 'MD5', 'Md5'])
def test_get_hash_md5(tmpdir, algorithm):
    check_get_hash(
        algorithm=algorithm,
        digest=hashlib.md5(),
        contents='testing 1 2 3'.encode(),
        tmpdir=tmpdir)


@pytest.mark.parametrize('algorithm', ['sha1', 'SHA1', 'Sha1'])
def test_get_hash_sha1(tmpdir, algorithm):
    check_get_hash(
        algorithm=algorithm,
        digest=hashlib.sha1(),
        contents='testing 1 2 3'.encode(),
        tmpdir=tmpdir)


@pytest.mark.parametrize('length,algorithm', [
    (1, 'sha224'),
    (44, 'sha224'),
    (45, 'sha256'),
    (51, 'sha256'),
    (52, 'sha384'),
    (76, 'sha384'),
    (77, 'sha512'),
    (102, 'sha512'),
])
def test_get_hash_sha2(tmpdir, length, algorithm):
    for algorithm_name in 'sha2', 'SHA2', 'Sha2':
        check_get_hash(
            algorithm=algorithm_name,
            length=length,
            digest=getattr(hashlib, algorithm)(),
            contents='testing 1 2 3'.encode(),
            tmpdir=tmpdir)
