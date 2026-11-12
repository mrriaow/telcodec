from telcodec import tbcd
from telcodec._common import validate_digits

INTERNATIONAL, UNKNOWN = 0x91, 0x81


def encode(number: str) -> bytes:
    if number.startswith("+"):
        type_byte, digits = INTERNATIONAL, number[1:]
    else:
        type_byte, digits = UNKNOWN, number

    validate_digits(digits, "MSISDN", 1, 15)

    return bytes([type_byte]) + tbcd.encode(digits)


def decode(data: bytes) -> str:
    if not data:
        raise ValueError("empty MSISDN, did you forget to put it in?")

    type_byte = data[0]

    if type_byte not in (INTERNATIONAL, UNKNOWN):
        raise ValueError(f"unsupported MSISDN type byte: {type_byte:#04x}")

    digits = tbcd.decode(data[1:])
    validate_digits(digits, "MSISDN", 1, 15)

    return ("+" if type_byte == INTERNATIONAL else "") + digits
