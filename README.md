# telcodec

small, strict encoders and decoders for telecom identifier and text formats. pure python, no dependencies.

| module | format | spec |
|---|---|---|
| `tbcd` | swapped-nibble digit strings | 3gpp ts 29.002 |
| `plmn` | mcc + mnc in 3 bytes | 3gpp ts 24.008 |
| `imsi` | sim subscriber identity | itu-t e.212 |
| `msisdn` | phone number with type byte | 3gpp ts 29.002 |
| `gsm7` | sms 7-bit alphabet and packing | 3gpp ts 23.038 |

## install

```
pip install .
```

## usage

```python
from telcodec import gsm7, imsi, msisdn, plmn, tbcd

tbcd.encode("12345").hex()  # '2143f5'
tbcd.decode(bytes.fromhex("2143f5"))  # '12345'

plmn.encode("310", "260").hex()  # '130062'
plmn.decode(bytes.fromhex("00f110"))  # ('001', '01')

imsi.split("001010123456789", 2)  # ('001', '01', '0123456789')

msisdn.encode("+14155550123").hex()  # '914151550521f3'

gsm7.encode("hello").hex()  # 'e8329bfd06'
gsm7.decode(bytes.fromhex("e8329bfd06"), 5)  # 'hello'
```

invalid input raises `ValueError`. decoders accept only bytes the matching encoder would produce.

## development

```
uv sync
uv run pytest
uv run ruff check
uv run mypy
```
