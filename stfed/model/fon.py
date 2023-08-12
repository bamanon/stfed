import dataclasses
import typing


@dataclasses.dataclass
class FontHeader:
    widest: int
    height: int
    ascent: int
    descent: int
    leading: int
    first_char: int
    last_char: int
    buf_width: int


@dataclasses.dataclass
class FontCharHeader:
    char_wide: int
    offset: int


@dataclasses.dataclass
class FontArrayElement:
    char_header: FontCharHeader
    char_data: bytes


@dataclasses.dataclass
class FontResource:
    header: FontHeader
    chars: typing.List[FontArrayElement]

