import io
import struct

import PIL.Image

import stfed.model
from stfed.consts import TILE_HEIGHT, TILE_WIDTH

def parse_tile_library(content: bytes) -> stfed.model.TlbTileLibrary:
    record_format = "=III64x"
    header_record_size = struct.calcsize(record_format)
    raw_bytes = content[0:header_record_size]
    gen_id, tiles_count, terrains_count = struct.unpack(record_format, raw_bytes)
    terrains = []
    terrain_format = "=20siiiiiIII"
    terrain_record_size = struct.calcsize(terrain_format)
    terrains_start = header_record_size
    for i in range(terrains_count):
        start = terrains_start + i * terrain_record_size
        end = start + terrain_record_size
        raw_bytes = content[start:end]
        record = struct.unpack(terrain_format, raw_bytes)
        last_byte = record[0].find(b"\x00")
        name = record[0][:last_byte].decode('utf-8')
        terrain = stfed.model.TlbTerrain(name, *record[1:])
        terrains.append(terrain)
    tiles = []
    tiles_start = header_record_size  + 128 * terrain_record_size
    tile_format = f"=BIII{TILE_HEIGHT * TILE_WIDTH}s"
    tile_record_size = struct.calcsize(tile_format)
    for i in range(tiles_count):
        start = tiles_start + i * tile_record_size
        end = start + tile_record_size
        raw_bytes = content[start:end]
        record = struct.unpack(tile_format, raw_bytes)
        terrain_type = stfed.model.TerrainType(record[0])
        tile = stfed.model.TlbTile(terrain_type, *record[1:])
        tiles.append(tile)
    tlb = stfed.model.TlbTileLibrary(gen_id, terrains, tiles)
    return tlb



def export_single_tile_image(
    tile: stfed.model.TlbTile,
    pal: stfed.model.Palette,
    side: stfed.model.Side=stfed.model.Side.SIDE1
) -> bytes:
    img = PIL.Image.new( 'RGB', (TILE_WIDTH, TILE_HEIGHT), "black")
    stfed.services.blt.blt(tile, 0, 0, img, pal, side=side, transparent=False)
    bytes_io = io.BytesIO()
    img.save(bytes_io, format='PNG')
    content = bytes_io.getvalue()
    return content
