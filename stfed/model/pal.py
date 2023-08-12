import dataclasses
import typing


@dataclasses.dataclass
class Palette:
    data: typing.List[typing.Tuple[int, int, int]]
    