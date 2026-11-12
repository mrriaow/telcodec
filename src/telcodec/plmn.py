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
