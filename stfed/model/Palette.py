import dataclasses


@dataclasses.dataclass
class Palette:
    data: list[(int, int, int)]
    