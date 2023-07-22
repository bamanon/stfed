import dataclasses 

@dataclasses.dataclass
class SquibResource():
    squibs: dict[int, str]

