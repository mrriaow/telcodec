import pytest
from hypothesis import given
from hypothesis import strategies as st

from telcodec import tbcd

VECTORS = [
    ("", ""),
    ("1", "f1"),
    ("12345", "2143f5"),
    ("*#abc", "badcfe"),
    ("001010123456789", "00010121436587f9"),
]

digit_strings = st.text(alphabet=tbcd.ALPHABET)


@pytest.mark.parametrize(("digits", "encoded"), VECTORS)
def test_encode_known_vectors(digits: str, encoded: str) -> None:
    assert tbcd.encode(digits).hex() == encoded


@pytest.mark.parametrize(("digits", "encoded"), VECTORS)
def test_decode_known_vectors(digits: str, encoded: str) -> None:
    assert tbcd.decode(bytes.fromhex(encoded)) == digits


@pytest.mark.parametrize("digits", ["12x", "1 2", "+123", "A", "d"])
def test_encode_rejects_characters_outside_alphabet(digits: str) -> None:
    with pytest.raises(ValueError):
        tbcd.encode(digits)


@pytest.mark.parametrize(
    "encoded",
    [
        "1f",  # filler in the low nibble
        "ff",  # filler in both nibbles
        "f1f2",  # filler before the last byte
        "21ff",  # low-nibble filler in the last byte
    ],
)
def test_decode_rejects_misplaced_filler(encoded: str) -> None:
    with pytest.raises(ValueError):
        tbcd.decode(bytes.fromhex(encoded))


@given(digit_strings)
def test_round_trip(digits: str) -> None:
    assert tbcd.decode(tbcd.encode(digits)) == digits


@given(digit_strings)
def test_encoded_length_is_half_the_digits_rounded_up(digits: str) -> None:
    assert len(tbcd.encode(digits)) == (len(digits) + 1) // 2


@given(st.binary())
def test_decode_accepts_only_bytes_that_encode_would_produce(data: bytes) -> None:
    try:
        digits = tbcd.decode(data)
    except ValueError:
        return
    assert tbcd.encode(digits) == data
