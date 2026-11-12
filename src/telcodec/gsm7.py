from typing import Any

ESCAPE = 0x1B

BASIC = (
    "@£$¥èéùìòÇ\nØø\rÅå"
    "Δ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ"
    " !\"#¤%&'()*+,-./"
    "0123456789:;<=>?"
    "¡ABCDEFGHIJKLMNO"
    "PQRSTUVWXYZÄÖÑÜ§"
    "¿abcdefghijklmno"
    "pqrstuvwxyzäöñüà"
)

EXTENSION = {
    "\f": 0x0A,
    "^": 0x14,
    "{": 0x28,
    "}": 0x29,
    "\\": 0x2F,
    "[": 0x3C,
    "~": 0x3D,
    "]": 0x3E,
    "|": 0x40,
    "€": 0x65,
}

_EXTENSION_CHARS = {code: ch for ch, code in EXTENSION.items()}


def to_septets(text: str) -> list[int]:
    septets: list[int] = []
    for ch in text:
        if ch in EXTENSION:
            septets.append(ESCAPE)
            septets.append(EXTENSION[ch])
        elif ch in BASIC and ch != "\x1b":
            septets.append(BASIC.index(ch))
        else:
            raise ValueError(f"not a GSM 7-bit character: {ch!r}")
    return septets


def from_septets(septets: list[int]) -> str:
    text: list[Any] = []
    i = 0
    while i < len(septets):
        code = septets[i]

        if not 0 <= code <= 0x7F:
            raise ValueError(f"not a 7-bit code: {code}")

        if code == ESCAPE:
            i += 1
            if i == len(septets):
                raise ValueError("escape code at the end of the data")
            if septets[i] not in _EXTENSION_CHARS:
                raise ValueError("escape code is not followed by an extension code")
            text.append(_EXTENSION_CHARS[septets[i]])
        else:
            text.append(BASIC[code])
        i += 1

    return "".join(text)


def pack(septets: list[int]) -> bytes:
    number = 0

    for i, code in enumerate(septets):
        if not 0 <= code <= 0x7F:
            raise ValueError(f"not a 7-bit code: {code}")

        number |= code << (7 * i)

    return number.to_bytes((7 * len(septets) + 7) // 8, "little")


def unpack(data: bytes, count: int) -> list[int]:
    if count < 0 or len(data) != (7 * count + 7) // 8:
        raise ValueError("length does not match count.")

    number = int.from_bytes(data, "little")

    if number >> (7 * count):
        raise ValueError("unused top bits are not zero!")

    return [(number >> (7 * i)) & 0x7F for i in range(count)]


def encode(text: str) -> bytes:
    return pack(to_septets(text))


def decode(data: bytes, septet_count: int) -> str:
    return from_septets(unpack(data, septet_count))
