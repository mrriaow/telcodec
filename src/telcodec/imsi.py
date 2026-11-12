from telcodec import tbcd
from telcodec._common import validate_digits


def encode(imsi: str) -> bytes:
    validate_digits(imsi, "IMSI", 6, 15)

    return tbcd.encode(imsi)


def decode(data: bytes) -> str:
    imsi = tbcd.decode(data)

    validate_digits(imsi, "IMSI", 6, 15)

    return imsi


def split(imsi: str, mnc_length: int) -> tuple[str, str, str]:
    validate_digits(imsi, "IMSI", 6, 15)

    if mnc_length not in (2, 3):
        raise ValueError("invalid MNC length. note: it's either 2 or 3 digits long.")

    return imsi[:3], imsi[3 : 3 + mnc_length], imsi[3 + mnc_length :]
