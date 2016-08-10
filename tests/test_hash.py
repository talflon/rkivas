import re
from random import Random

import hypothesis.strategies as hs
from hypothesis import given, assume

from rkivas import hash_file, encode_hash


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
