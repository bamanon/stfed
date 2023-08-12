import dataclasses
import typing

from stfed.model.TerrainType import TerrainType


@dataclasses.dataclass
class TlbTerrain:
    name: str
    move_rate: int
    attack_mod: int
    attack_range_mod: int
    defense_mod: int
    damage_val: int
    color: int
    burnable: int
    portrait_num: int


@dataclasses.dataclass
class TlbTile:
    terrain_type: TerrainType
    swap_tile: int
    ani_res: int
    ani_delay: int
    bitmap: bytes


@dataclasses.dataclass
class TlbTileLibrary:
    gen_id: int
    terrains: typing.List[TlbTerrain]
    tiles: typing.List[TlbTile]

