import pytest
from hypothesis import given
from hypothesis import strategies as st

from telcodec import imsi

VECTORS = [
    ("001010123456789", "00010121436587f9"),
    ("310260123456789", "13200621436587f9"),
    ("00101012345678", "00010121436587"),
    ("001011", "000111"),
]

imsis = st.text(alphabet="0123456789", min_size=6, max_size=15)


@pytest.mark.parametrize(("digits", "encoded"), VECTORS)
def test_encode_known_vectors(digits: str, encoded: str) -> None:
    assert imsi.encode(digits).hex() == encoded


@pytest.mark.parametrize(("digits", "encoded"), VECTORS)
def test_decode_known_vectors(digits: str, encoded: str) -> None:
    assert imsi.decode(bytes.fromhex(encoded)) == digits


@pytest.mark.parametrize(
    "digits",
    [
        "",
        "00101",  # 5 digits: too short
        "0010101234567890",  # 16 digits: too long
        "00101*123456789",  # legal in TBCD, not in an IMSI
        "0010a0123456789",
        "001 010123456789",
    ],
)
def test_encode_rejects_invalid_imsi(digits: str) -> None:
    with pytest.raises(ValueError):
        imsi.encode(digits)


@pytest.mark.parametrize(
    "encoded",
    [
        "",
        "0001f1",  # 5 digits: too short
        "0001012143658709",  # 16 digits: too long
        "0a0101214365",  # contains '*'
        "00c101214365",  # contains 'a'
        "00f101214365",  # filler before the last byte
    ],
)
def test_decode_rejects_invalid_bytes(encoded: str) -> None:
    with pytest.raises(ValueError):
        imsi.decode(bytes.fromhex(encoded))


@pytest.mark.parametrize(
    ("digits", "mnc_length", "parts"),
    [
        ("001010123456789", 2, ("001", "01", "0123456789")),
        ("001010123456789", 3, ("001", "010", "123456789")),
        ("310260123456789", 3, ("310", "260", "123456789")),
        ("001011", 2, ("001", "01", "1")),
    ],
)
def test_split(digits: str, mnc_length: int, parts: tuple[str, str, str]) -> None:
    assert imsi.split(digits, mnc_length) == parts


@pytest.mark.parametrize(
    ("digits", "mnc_length"),
    [
        ("001010123456789", 1),
        ("001010123456789", 4),
        ("00101", 2),  # not a valid IMSI
        ("00101*123456789", 2),
    ],
)
def test_split_rejects_invalid_input(digits: str, mnc_length: int) -> None:
    with pytest.raises(ValueError):
        imsi.split(digits, mnc_length)


@given(imsis)
def test_round_trip(digits: str) -> None:
    assert imsi.decode(imsi.encode(digits)) == digits


@given(imsis, st.sampled_from([2, 3]))
def test_split_parts_rejoin_to_the_imsi(digits: str, mnc_length: int) -> None:
    mcc, mnc, msin = imsi.split(digits, mnc_length)
    assert (len(mcc), len(mnc)) == (3, mnc_length)
    assert mcc + mnc + msin == digits


@given(st.binary(max_size=9))
def test_decode_accepts_only_bytes_that_encode_would_produce(data: bytes) -> None:
    try:
        digits = imsi.decode(data)
    except ValueError:
        return
    assert imsi.encode(digits) == data
