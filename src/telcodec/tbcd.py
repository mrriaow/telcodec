"""
a TBCD (telephony binary-coded decimal) encode/decode tool

low nibble first, 0xF filler, per 3GPP TS 29.002
"""

from telcodec._common import FILLER, swap_pairs

ALPHABET = "0123456789*#abc"

_TO_HEX = str.maketrans("*#abc", "abcde")
_FROM_HEX = str.maketrans("abcde", "*#abc")


def encode(digits: str) -> bytes:
    """
    encode function, it takes the digits passed to it, translates it
    according to the table set above, swaps every 2 numbers to match
    TBCDs, ecodes it to bytes and returns the value

    usage example: tbcd.encode("14155550123")
    """
    for ch in digits:
        if ch not in ALPHABET:
            raise ValueError(f"invalid TBCD character: {ch!r}")

    hex_chars = digits.translate(_TO_HEX)
    if len(hex_chars) % 2:
        hex_chars += FILLER

    swapped = swap_pairs(hex_chars)

    return bytes.fromhex(swapped)


def decode(data: bytes) -> str:
    """
    decode functions, takes the data passed to it, translates it
    according to the table also set above (xd) swaps every 2 numbers
    yet again to match back to the initial data, encodes it to hex,
    returns the value

    usage example: tbcd.decode(bytes.fromhex("4151550521f3"))
    """
    hex_chars = data.hex().translate(_FROM_HEX)
    original_hex = swap_pairs(hex_chars)

    if original_hex.endswith(FILLER):
        original_hex = original_hex[:-1]

    for ch in original_hex:
        if ch not in ALPHABET:
            raise ValueError(f"invalid TBCD character: {ch!r}")

    return original_hex
