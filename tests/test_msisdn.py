import pytest
from hypothesis import given
from hypothesis import strategies as st

from telcodec import msisdn

VECTORS = [
    ("+14155550123", "914151550521f3"),
    ("14155550123", "814151550521f3"),
    ("+447700900123", "91447700091032"),
    ("+1", "91f1"),
    ("0", "81f0"),
]

numbers = st.builds(
    lambda plus, digits: plus + digits,
    st.sampled_from(["", "+"]),
    st.text(alphabet="0123456789", min_size=1, max_size=15),
)


@pytest.mark.parametrize(("number", "encoded"), VECTORS)
def test_encode_known_vectors(number: str, encoded: str) -> None:
    assert msisdn.encode(number).hex() == encoded


@pytest.mark.parametrize(("number", "encoded"), VECTORS)
def test_decode_known_vectors(number: str, encoded: str) -> None:
    assert msisdn.decode(bytes.fromhex(encoded)) == number


@pytest.mark.parametrize(
    "number",
    [
        "",
        "+",  # no digits
        "+1234567890123456",  # 16 digits: too long
        "1234567890123456",
        "+1415555012a",  # legal in TBCD, not in a phone number
        "+14155*",
        "+1 415 555 0123",
        "++14155550123",
        "1415+5550123",  # "+" is only legal in front
    ],
)
def test_encode_rejects_invalid_numbers(number: str) -> None:
    with pytest.raises(ValueError):
        msisdn.encode(number)


@pytest.mark.parametrize(
    "encoded",
    [
        "",  # no type byte
        "91",  # type byte but no digits
        "4151550521f3",  # digits with no type byte in front
        "a14151550521f3",  # unsupported type byte
        "912143658709214365",  # 16 digits: too long
        "91a1",  # contains '*'
        "91f1f2",  # filler before the last byte
    ],
)
def test_decode_rejects_invalid_bytes(encoded: str) -> None:
    with pytest.raises(ValueError):
        msisdn.decode(bytes.fromhex(encoded))


def test_plus_changes_only_the_type_byte() -> None:
    assert msisdn.encode("+14155550123")[1:] == msisdn.encode("14155550123")[1:]
    assert msisdn.encode("+14155550123")[0] != msisdn.encode("14155550123")[0]


@given(numbers)
def test_round_trip(number: str) -> None:
    assert msisdn.decode(msisdn.encode(number)) == number


@given(st.binary(max_size=10))
def test_decode_accepts_only_bytes_that_encode_would_produce(data: bytes) -> None:
    try:
        number = msisdn.decode(data)
    except ValueError:
        return
    assert msisdn.encode(number) == data
