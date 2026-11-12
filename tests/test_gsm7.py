import pytest
from hypothesis import given
from hypothesis import strategies as st

from telcodec import gsm7

ALPHABET = gsm7.BASIC.replace("\x1b", "") + "".join(gsm7.EXTENSION)

texts = st.text(alphabet=ALPHABET)
codes = st.lists(st.integers(min_value=0, max_value=0x7F))


# Stage 1: characters <-> septets


@pytest.mark.parametrize(
    ("char", "code"),
    [
        ("@", 0x00),
        ("£", 0x01),
        ("$", 0x02),
        ("Ç", 0x09),
        ("\n", 0x0A),
        ("Δ", 0x10),
        ("_", 0x11),
        ("ß", 0x1E),
        (" ", 0x20),
        ("A", 0x41),
        ("¿", 0x60),
        ("a", 0x61),
        ("à", 0x7F),
    ],
)
def test_to_septets_basic_table(char: str, code: int) -> None:
    assert gsm7.to_septets(char) == [code]


@pytest.mark.parametrize(
    ("char", "code"),
    [
        ("\f", 0x0A),
        ("^", 0x14),
        ("{", 0x28),
        ("}", 0x29),
        ("\\", 0x2F),
        ("[", 0x3C),
        ("~", 0x3D),
        ("]", 0x3E),
        ("|", 0x40),
        ("€", 0x65),
    ],
)
def test_to_septets_extension_table(char: str, code: int) -> None:
    assert gsm7.to_septets(char) == [gsm7.ESCAPE, code]


def test_to_septets_keeps_character_order() -> None:
    assert gsm7.to_septets("Hi €5") == [0x48, 0x69, 0x20, 0x1B, 0x65, 0x35]


@pytest.mark.parametrize(
    "text",
    [
        "\x1b",  # the escape code is not a character
        "`",
        "ç",  # only the capital is in the table
        "\t",
        "\x00",
        "Ą",
        "😀",
        "hello`",
    ],
)
def test_to_septets_rejects_characters_outside_alphabet(text: str) -> None:
    with pytest.raises(ValueError):
        gsm7.to_septets(text)


@pytest.mark.parametrize(
    "septets",
    [
        [0x1B],  # escape with nothing after it
        [0x41, 0x1B],
        [0x1B, 0x41],  # escape followed by a code that is not in the extension table
        [0x1B, 0x1B],
        [0x80],  # does not fit in 7 bits
        [-1],
        [0x41, 200],
    ],
)
def test_from_septets_rejects_invalid_codes(septets: list[int]) -> None:
    with pytest.raises(ValueError):
        gsm7.from_septets(septets)


@given(texts)
def test_septets_round_trip(text: str) -> None:
    assert gsm7.from_septets(gsm7.to_septets(text)) == text


@given(codes)
def test_from_septets_accepts_only_what_to_septets_would_produce(septets: list[int]) -> None:
    try:
        text = gsm7.from_septets(septets)
    except ValueError:
        return
    assert gsm7.to_septets(text) == septets


# Stage 2: septets <-> bytes

PACKED = [
    ([], ""),
    ([0x00], "00"),
    ([0x7F], "7f"),
    ([0x7F, 0x7F], "ff3f"),
    ([0x01, 0x02, 0x03], "01c100"),
    ([0x7F] * 8, "ffffffffffffff"),
    ([0x68, 0x65, 0x6C, 0x6C, 0x6F], "e8329bfd06"),
]


@pytest.mark.parametrize(("values", "encoded"), PACKED)
def test_pack_known_vectors(values: list[int], encoded: str) -> None:
    assert gsm7.pack(values).hex() == encoded


@pytest.mark.parametrize(("values", "encoded"), PACKED)
def test_unpack_known_vectors(values: list[int], encoded: str) -> None:
    assert gsm7.unpack(bytes.fromhex(encoded), len(values)) == values


@pytest.mark.parametrize("values", [[0x80], [-1], [0x41, 200]])
def test_pack_rejects_out_of_range_values(values: list[int]) -> None:
    with pytest.raises(ValueError):
        gsm7.pack(values)


@pytest.mark.parametrize(
    ("encoded", "count"),
    [
        ("", 1),  # too few bytes for the count
        ("e8329bfd06", 6),
        ("e8329bfd06", 4),  # too many bytes for the count
        ("00", 0),
        ("ff", 1),  # unused top bit is not zero
        ("e8329bfd0e", 5),
        ("", -1),
        ("00", -1),
    ],
)
def test_unpack_rejects_inconsistent_input(encoded: str, count: int) -> None:
    with pytest.raises(ValueError):
        gsm7.unpack(bytes.fromhex(encoded), count)


@given(codes)
def test_pack_round_trip(values: list[int]) -> None:
    assert gsm7.unpack(gsm7.pack(values), len(values)) == values


@given(codes)
def test_packed_length_is_seven_eighths_rounded_up(values: list[int]) -> None:
    assert len(gsm7.pack(values)) == (7 * len(values) + 7) // 8


@given(st.binary(max_size=20), st.integers(min_value=0, max_value=24))
def test_unpack_accepts_only_what_pack_would_produce(data: bytes, count: int) -> None:
    try:
        values = gsm7.unpack(data, count)
    except ValueError:
        return
    assert gsm7.pack(values) == data


# Stage 3: text <-> bytes

ENCODED = [
    ("", 0, ""),
    ("hello", 5, "e8329bfd06"),
    ("hellohello", 10, "e8329bfd4697d9ec37"),
    ("How are you?", 12, "c8f71d14969741f977fd07"),
    ("€", 2, "9b32"),
    ("[]", 4, "1bdec607"),
    ("{€}", 6, "1bd4a6bc4901"),
]


@pytest.mark.parametrize(("text", "count", "encoded"), ENCODED)
def test_encode_known_vectors(text: str, count: int, encoded: str) -> None:
    assert gsm7.encode(text).hex() == encoded


@pytest.mark.parametrize(("text", "count", "encoded"), ENCODED)
def test_decode_known_vectors(text: str, count: int, encoded: str) -> None:
    assert gsm7.decode(bytes.fromhex(encoded), count) == text


@pytest.mark.parametrize(
    ("encoded", "count"),
    [
        ("e8329bfd06", 4),  # count does not match the length
        ("9b", 1),  # unused top bit is not zero
        ("1b", 1),  # escape with nothing after it
    ],
)
def test_decode_rejects_invalid_input(encoded: str, count: int) -> None:
    with pytest.raises(ValueError):
        gsm7.decode(bytes.fromhex(encoded), count)


def test_decode_needs_the_count_to_tell_padding_from_an_at_sign() -> None:
    data = bytes.fromhex("31d98c56b3dd00")
    assert gsm7.encode("1234567") == gsm7.encode("1234567@") == data
    assert gsm7.decode(data, 7) == "1234567"
    assert gsm7.decode(data, 8) == "1234567@"


def test_160_characters_fit_in_140_bytes() -> None:
    assert len(gsm7.encode("a" * 160)) == 140


@given(texts)
def test_encode_decode_round_trip(text: str) -> None:
    assert gsm7.decode(gsm7.encode(text), len(gsm7.to_septets(text))) == text
