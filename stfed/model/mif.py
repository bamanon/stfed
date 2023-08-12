import dataclasses
import enum
import typing

from stfed.model.Side import Side
from stfed.model.TerrainType import TerrainType


class ItemType(enum.Enum):
    #NO_ITEM = 0
    BERSERKER_BREW = 1
    BOAR_BURGER = 2
    BOG_BOOTS = 3
    DAEMONS_BANE = 4
    DOWRY_CHEST = 5
    DRIFT_DISC = 6
    FROST_CAPE = 7
    HEALING_SALVE = 8
    KEY = 9
    MAP = 10
    MIGHT_MANTLE = 11
    SACRED_URN = 12
    COMPONENT = 13
    SHRUB_SPRITE = 14
    STORM_BRACERS = 15
    TELEPORT_TOME = 16
    TRAILFINDER = 17
    VERDANT_SHIELD = 18
    VIRTUE_VEIL = 19
    WEIRD_WAND = 20
    MASON_MIX = 21
    MANA_ORB = 22
    HARPY_NET = 23
    WEIRD_WARD =  24
    #ENDOFITEMTYPES = 25


class FuncType(enum.Enum):
    FUNC_MISC = 0
    FUNC_ARBORLODGE = enum.auto()
    FUNC_BARRACKS = enum.auto()
    FUNC_CRYPT = enum.auto()
    FUNC_RUNESTONE = enum.auto()
    FUNC_TEMPLE = enum.auto()
    FUNC_FLAMESPOUT = enum.auto()
    FUNC_MINESHAFT = enum.auto()
    FUNC_PORTAL = enum.auto() #a bforge
    FUNC_WHIRLPOOL = enum.auto()
    FUNC_HOME = enum.auto()
    FUNC_ARBOR_FOUND = enum.auto()
    FUNC_BARRACKS_FOUND = enum.auto()
    FUNC_CRYPT_FOUND = enum.auto()
    FUNC_RUNE_FOUND = enum.auto()
    FUNC_TEMPLE_FOUND = enum.auto()
    FUNC_KEEP = enum.auto()
    FUNC_AQUEDUCT = enum.auto()
    FUNC_GATE = enum.auto()
    FUNC_CAMP = enum.auto()
    FUNC_CAULDRON = enum.auto()
    FUNC_SWTRIP = enum.auto()
    FUNC_SWPRESSURE = enum.auto()
    FUNC_IMM_GATE = enum.auto()
    FUNC_IMM_WELL = enum.auto()
    FUNC_GEN_FOUND = enum.auto()
    FUNC_BANISH_STONE = enum.auto()
    FUNC_PRISON_PIT = enum.auto()
    #TOTALFUNCTIONS = enum.auto()
    

@dataclasses.dataclass
class MifSpaceInfo:
    func_type: FuncType
    x_pos: int
    y_pos: int
    dest_x: int #TODO: investigate use
    dest_y: int
    owner: Side
    max_hp: int
    preset_item: typing.Optional[ItemType]
    hot_spot: bool #ai will guard this area
    pick_random_item: bool #an item lying under a building
    special_item_drop: bool #an item lying on the ground
    placements: typing.List[typing.Tuple[int, int, int, int]]


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
    transform_cost: typing.Optional[int]
    transform_time: typing.Optional[int]
    exp_required: typing.Optional[int]
    exp_gained: typing.Optional[int]
    research_time: typing.Optional[int]


@dataclasses.dataclass
class MifUnitPlacement:
    name: str
    owner: Side
    position: typing.Union[str, typing.Tuple[int, int]]
    count: int
    sleeper: bool
    start_hp: typing.Optional[int]

@dataclasses.dataclass
class MifItemPlacement:
    item_type: ItemType
    count: int
    position: typing.Optional[typing.Tuple[int, int]]
    terrain_type: typing.Optional[TerrainType]


@dataclasses.dataclass
class MifMapInfoRes:
    gen_id: int
    config_lines: typing.List[str]
    map_tiles: typing.List[int]
    map_spaces: typing.List[int] #TODO: potentially no longer required after building spaces.placements
    spaces: typing.List[MifSpaceInfo]
    unitlib: typing.List[MifUnitLibEntry]
    units: typing.List[MifUnitPlacement]
    rand_units: typing.List[MifUnitPlacement]
    item_placements: typing.List[MifItemPlacement]

