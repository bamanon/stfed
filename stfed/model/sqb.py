import dataclasses 
import typing


@dataclasses.dataclass
class SquibResource():
    resource_name: int
    squibs:typing.Dict[int, str]

