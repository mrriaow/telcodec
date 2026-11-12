"""PLMN identity (MCC + MNC) packed into 3 bytes, per 3GPP TS 24.008 section 10.5.1.3.

Each cell is one nibble, written high | low:

    byte 1:  MCC digit 2 | MCC digit 1
    byte 2:  MNC digit 3 | MCC digit 3     (MNC digit 3 is 0xF for a 2-digit MNC)
    byte 3:  MNC digit 2 | MNC digit 1

    ("310", "260")  ->  0x13 0x00 0x62
    ("001", "01")   ->  0x00 0xF1 0x10
"""

from telcodec._common import FILLER, swap_pairs, validate_digits


def encode(mcc: str, mnc: str) -> bytes:
    validate_digits(mcc, "MCC", 3, 3)
    validate_digits(mnc, "MNC", 2, 3)

    # third is last letter in mnc if mnc is 3 digits, otherwise its filler
    third = mnc[2] if len(mnc) == 3 else FILLER
    # format:                  mcc 3 digits + last mnc digit + the last mnc digits
    return bytes.fromhex(swap_pairs(mcc + third + mnc[:2]))


def decode(data: bytes) -> tuple[str, str]:
    if len(data) != 3:
        raise ValueError("invalid PLMN. bytes are not 3.")

    s = swap_pairs(data.hex())  # [ MCC1 | MCC2 ] [ MCC3 | MNC3 ] [ MNC1 | MNC2 ]

    mcc = s[0:3]
    mnc = s[4:6]

    if s[3] != FILLER:
        mnc += s[3]

    validate_digits(mcc, "MCC", 3, 3)
    validate_digits(mnc, "MNC", 2, 3)

    return mcc, mnc
