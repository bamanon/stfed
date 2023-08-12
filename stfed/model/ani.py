import dataclasses
import typing


@dataclasses.dataclass
class CelHeader():
    org_x: int
    org_y: int
    width: int
    height: int
    priority: int
    offset: int


@dataclasses.dataclass
class CelResource():
    header: CelHeader
    data: bytes


@dataclasses.dataclass
class AniResource():
    cels: typing.List[CelResource]
