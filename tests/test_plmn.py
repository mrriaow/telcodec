import pytest
from hypothesis import given
from hypothesis import strategies as st

from telcodec import plmn

VECTORS = [
    ("310", "260", "130062"),
    ("310", "410", "130014"),
    ("001", "01", "00f110"),
    ("001", "001", "001100"),
    ("208", "01", "02f810"),
    ("234", "15", "32f451"),
]

mccs = st.text(alphabet="0123456789", min_size=3, max_size=3)
mncs = st.text(alphabet="0123456789", min_size=2, max_size=3)


@pytest.mark.parametrize(("mcc", "mnc", "encoded"), VECTORS)
def test_encode_known_vectors(mcc: str, mnc: str, encoded: str) -> None:
    assert plmn.encode(mcc, mnc).hex() == encoded


@pytest.mark.parametrize(("mcc", "mnc", "encoded"), VECTORS)
def test_decode_known_vectors(mcc: str, mnc: str, encoded: str) -> None:
    assert plmn.decode(bytes.fromhex(encoded)) == (mcc, mnc)


@pytest.mark.parametrize(
    ("mcc", "mnc"),
    [
        ("31", "260"),  # MCC too short
        ("3100", "260"),  # MCC too long
        ("310", "2"),  # MNC too short
        ("310", "2600"),  # MNC too long
        ("310", ""),
        ("31a", "260"),  # not a decimal digit
        ("310", "2f"),
        ("310", "2*"),
    ],
)
def test_encode_rejects_invalid_codes(mcc: str, mnc: str) -> None:
    with pytest.raises(ValueError):
        plmn.encode(mcc, mnc)


@pytest.mark.parametrize(
    "encoded",
    [
        "",  # wrong length
        "1300",
        "13006200",
        "1f0062",  # filler in MCC digit 1
        "f30062",  # filler in MCC digit 2
        "130f62",  # filler in MCC digit 3
        "1300f2",  # filler in MNC digit 2
        "13006f",  # filler in MNC digit 1
        "13a062",  # non-decimal nibble in MNC digit 3
        "1a0062",  # non-decimal nibble in MCC digit 1
    ],
)
def test_decode_rejects_invalid_bytes(encoded: str) -> None:
    with pytest.raises(ValueError):
        plmn.decode(bytes.fromhex(encoded))


def test_two_and_three_digit_mnc_are_distinct() -> None:
    assert plmn.encode("001", "01") != plmn.encode("001", "001")
    assert plmn.encode("001", "01") != plmn.encode("001", "010")


@given(mccs, mncs)
def test_round_trip(mcc: str, mnc: str) -> None:
    assert plmn.decode(plmn.encode(mcc, mnc)) == (mcc, mnc)


@given(st.binary(min_size=3, max_size=3))
def test_decode_accepts_only_bytes_that_encode_would_produce(data: bytes) -> None:
    try:
        mcc, mnc = plmn.decode(data)
    except ValueError:
        return
    assert plmn.encode(mcc, mnc) == data
