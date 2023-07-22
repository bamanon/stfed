import dataclasses
import dataclasses
import typing
import dataclasses
import typing

from stfed.model.Side import Side
from stfed.model.FuncType import FuncType
from stfed.model.ItemType import ItemType
from stfed.model.TerrainType import TerrainType

@dataclasses.dataclass
class MifSpaceInfo:
    func_type: FuncType
    x_pos: int
    y_pos: int
    dest_x: int #TODO: investigate use
    dest_y: int
    owner: Side
    max_hp: int
    preset_item: ItemType|None
    hot_spot: bool #ai will guard this area
    pick_random_item: bool #an item lying under a building
    special_item_drop: bool #an item lying on the ground
    placements: list[(int, int, int, int)]


@dataclasses.dataclass
class MifUnitLibEntry:
    internal_name: str
    base_move_rate: int
    movement_type: str #TODO: model.MovementType
    max_hp: int
    base_attack: int
    base_defense: int
    base_attack_range: int
    base_anim: int
    portrait_anim: int
    skill_range: int
    skill_cost: int
    transform_cost: int|None
    transform_time: int|None
    exp_required: int|None
    exp_gained: int|None
    research_time: int|None


@dataclasses.dataclass
class MifUnitPlacement:
    name: str
    owner: Side
    position: str|typing.Tuple[int, int]
    count: int
    sleeper: bool
    start_hp: int|None

@dataclasses.dataclass
class MifItemPlacement:
    item_type: ItemType
    count: int
    position: typing.Tuple[int, int]|None
    terrain_type: TerrainType|None


@dataclasses.dataclass
class MifMapInfoRes:
    gen_id: int
    config_lines: list[str]
    map_tiles: list[int]
    map_spaces: list[int] #TODO: potentially no longer required after building spaces.placements
    spaces: list[MifSpaceInfo]
    unitlib: list[MifUnitLibEntry]
    units: list[MifUnitPlacement]
    rand_units: list[MifUnitPlacement]
    item_placements: list[MifItemPlacement]

