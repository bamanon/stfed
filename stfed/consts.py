import os.path


basedir = os.path.dirname(__file__)


STFED_VERSION = "0.1"

TILE_WIDTH = 20
TILE_HEIGHT = 38
WORLD_HEIGHT = 40
WORLD_WIDTH = 32
WORLD_SIZE = WORLD_WIDTH * WORLD_HEIGHT

UNIT_COLORS_START = 192
UNIT_COLORS_LENGTH = 8
UNIT_COLORS_END = UNIT_COLORS_START + UNIT_COLORS_LENGTH
# needed to recolor hostile wizards and rangers in the final legendary mission. where the hell does this happen in src though
HOSTILE_COLORS_START = 48 + 2
