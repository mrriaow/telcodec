"""Shared helpers for the telcodec modules."""

DIGITS = "0123456789"
FILLER = "f"


def swap_pairs(text: str) -> str:
    """Swap each pair of characters: "2143f5" -> "12345f"."""
    return "".join(text[i + 1] + text[i] for i in range(0, len(text), 2))


def validate_digits(value: str, name: str, min_length: int, max_length: int) -> None:
    """Raise ValueError unless value is min_length to max_length decimal digits."""
    if not min_length <= len(value) <= max_length:
        raise ValueError(f"invalid {name} length: {len(value)}")
    for ch in value:
        if ch not in DIGITS:
            raise ValueError(f"invalid {name} character: {ch!r}")
