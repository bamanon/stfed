import io
import typing 
import struct

import PIL.Image

import stfed.model
from stfed.model.TerrainType import walkable as walkable_terrain_types
import stfed.consts
import stfed.services.blt


MAX_CONFIG_LINES = 130
CONFIG_LINE_MAX_LEN = 80


def parse_map_info_res(content: bytes):
    map_info_header_format = f"=I{MAX_CONFIG_LINES*CONFIG_LINE_MAX_LEN}sI128x{stfed.consts.WORLD_SIZE*2}s{stfed.consts.WORLD_SIZE*2}sI"
    map_info_header_size = struct.calcsize(map_info_header_format)
    start = 0
    end = map_info_header_size
    raw = content[start:end]
    record = struct.unpack(map_info_header_format, raw)
    
    gen_id = record[0]
    
    total_config_lines = record[2]
    config_lines = record[1]
    config_lines = [
        line[0].decode('utf-8').rstrip('\x00')
        for line in struct.iter_unpack(f"={CONFIG_LINE_MAX_LEN}s", config_lines)
    ][:total_config_lines]

    map_tiles = record[3]
    map_tiles = list(struct.unpack(f"={stfed.consts.WORLD_SIZE}h", map_tiles))
    
    map_spaces = record[4]
    map_spaces = list(struct.unpack(f"={stfed.consts.WORLD_SIZE}h", map_spaces))

    #spaces_count = record[5]
    #TODO: is assumption always correct?
    # space_size = len(content) - map_info_header_size / spaces_count # 271
    space_format = "=B 7i 3B 239x"
    #space_size = struct.calcsize(space_format)
    #TODO: should we end at map_info_header_size + space_size * spaces_count?
    raw = content[map_info_header_size:]

    unitlib = __parse_unit_libs(config_lines)
    units, rand_units = __parse_units(config_lines)
    item_placements = __parse_item_placements(config_lines)

    spaces = [
        stfed.model.MifSpaceInfo(
            stfed.model.FuncType(t[0]),
            *t[1:5],
            stfed.model.Side(t[5]),
            t[6],
            __pick_item_type(t[7]),
            bool(t[8]), 
            bool(t[9]), 
            bool(t[10]),
            __pick_placements(map_spaces, i))
        for i, t in enumerate(struct.iter_unpack(space_format, raw))
    ]

    mif = stfed.model.MifMapInfoRes(gen_id, config_lines, map_tiles, map_spaces, spaces, unitlib, units, rand_units, item_placements)
    return mif



def __pick_item_type(s: str) -> stfed.model.ItemType|None:
    item_id = int(s)
    if item_id == 0:
        return None
    return stfed.model.ItemType(item_id)

def __parse_units(
        config_lines: typing.List[str]
) -> typing.List[stfed.model.MifUnitPlacement]:
    entries = []
    randunits_entries = []
    before = True
    is_randunit = False
    for line in config_lines:
        if before:
            if line == '#UNITS':
                before = False
        elif line == '#RANDUNITS':
            is_randunit = True
        else:
            if line[:2] != '# ':
                break
            tokens = line.split(' ')
            owner = [
                stfed.model.Side.NEUTRAL,
                stfed.model.Side.SIDE1,
                stfed.model.Side.SIDE2,
                stfed.model.Side.HOSTILE
            ][int(tokens[2])]
            position = tokens[3]
            if position != 'DEFAULT':
                parts  = position.split(',')
                position = (int(parts[0]), int(parts[1]))
            count = int(tokens[4])
            start_hp = None
            sleeper = False
            if len(tokens) == 6:
                if tokens[5] == 'SLEEP':
                    sleeper = True
                else:
                    start_hp = int(tokens[5])
            entry = stfed.model.MifUnitPlacement(
                tokens[1],
                owner,
                position,
                count,
                sleeper,
                start_hp
            )
            if is_randunit:
                randunits_entries.append(entry)
            else:
                entries.append(entry)
    return entries, randunits_entries


def __parse_unit_libs(
        config_lines: typing.List[str]
) -> typing.List[stfed.model.MifUnitLibEntry]:
    entries = []
    before = True
    for line in config_lines:
        if before:
            if line == '#UNITLIB':
                before = False
        else:
            if line[:2] != '# ':
                return entries
            tokens = line.split(' ')
            entry = stfed.model.MifUnitLibEntry(
                tokens[1],
                int(tokens[2]),
                tokens[3],
                *[int(t) for t in tokens[4:10]],
                *[int(t) if t is not None else None for t in tokens[10:]],
            )
            entries.append(entry)
    return entries


def __parse_item_placements(
        config_lines: typing.List[str]
) -> typing.List[stfed.model.MifItemPlacement]:
    entries = []
    for line in config_lines:
        if not line.startswith("#PLACEITEM "):
            continue
        tokens = line.split(' ')
        escaped_type = tokens[1].replace('\'', '')
        item_type = getattr(stfed.model.ItemType, escaped_type)
        count = 1
        terrain_type = None
        pos = None
        if tokens[3].isnumeric():
            pos = int(tokens[2]), int(tokens[3])
        else:
            count = int(tokens[2])
            terrain_type = getattr(stfed.model.TerrainType, tokens[3])
        entries.append(stfed.model.MifItemPlacement(item_type, count, pos, terrain_type))
    return entries


def __pick_placements(
        map_spaces: typing.List[int], 
        id: int
) -> typing.List[typing.Tuple[int, int, int, int]]:
    if id == 0:
        return []
    points = []
    for y in range(stfed.consts.WORLD_HEIGHT):
        for x in range(stfed.consts.WORLD_WIDTH):
            if map_spaces[y * stfed.consts.WORLD_WIDTH + x] == id:
                points.append((x, y))
    #TODO: group into rects/polygons where possible
    results = [
        (*p, 1, 1)
        for p in points
    ]
    return results


def export_random_items_preview(
        mif: stfed.model.MifMapInfoRes,
        pal: stfed.model.Palette,
        itemlib: dict[stfed.model.ItemType, stfed.model.AniResource]
):
    entries: list[stfed.model.MifItemPlacement] = [
        e
        for p in mif.item_placements
        for e in [p]*p.count
    ]
    if len(entries) == 0:
        return None
    image_width = stfed.consts.TILE_WIDTH * len(entries)
    image_height = stfed.consts.TILE_HEIGHT
    img = PIL.Image.new('RGBA', (image_width, image_height))
    for i, entry in enumerate(entries):
        ani = itemlib[entry.item_type]
        stfed.services.blt.blt(ani, i, 0, img, pal, alignment=stfed.services.blt.Alignment.CENTER)
    bytes_io = io.BytesIO()
    img.save(bytes_io, format='PNG')
    content = bytes_io.getvalue()
    return content

def export_preview_image(
        mif: stfed.model.MifMapInfoRes,
        tlb: stfed.model.TlbTileLibrary,
        pal: stfed.model.Palette,
        unitlib: dict[str, stfed.model.AniResource],
        itemlib: dict[stfed.model.ItemType, stfed.model.AniResource]
) -> bytes:
    map_width = stfed.consts.WORLD_WIDTH * stfed.consts.TILE_WIDTH
    map_height = stfed.consts.WORLD_HEIGHT * stfed.consts.TILE_HEIGHT
    img = PIL.Image.new('RGBA', (map_width, map_height))
    random_item_img = PIL.Image.open("resources/random-item.png")
    random_item_on_raze_img = PIL.Image.open("resources/random-item-on-raze.png")
    randunit_img = PIL.Image.open("resources/randunit.png")
    default_placement_img = PIL.Image.open("resources/default-placement.png")

    for row in range(stfed.consts.WORLD_HEIGHT):
        for col in range(stfed.consts.WORLD_WIDTH):
            i = row * stfed.consts.WORLD_WIDTH + col
            tid = mif.map_tiles[i]
            tile = tlb.tiles[tid]

            side = stfed.model.Side.SIDE1
            space_id = mif.map_spaces[i]
            space = None
            if space_id > 0:
                space = mif.spaces[space_id]
            if space is not None:
                side = space.owner
            stfed.services.blt.blt(tile, col, row, img, pal, transparent=False, side=side)

    all_units = [y for x in [[(u, False)]*u.count for u in mif.units] + [[(u, True)]*u.count for u in mif.rand_units] for y in x]
    default_placements = __find_default_placements(mif, tlb)
    for unit, is_rand_unit in all_units:
        if unit.position != 'DEFAULT':
            placement = unit.position[0], unit.position[1]
        else:
            placement = default_placements[unit.owner].pop()

        side = unit.owner
        unitlib_entry = unitlib[unit.name]
        cel = unitlib_entry.cels[0]
        stfed.services.blt.blt(cel, placement[0], placement[1], img, pal, side=side, alignment=stfed.services.blt.Alignment.BOTTOM_CENTER)
        # if is_rand_unit:
        #     stfed.services.blt.blt(randunit_img, placement[0], placement[1], img, pal, side=side, alignment=stfed.services.blt.Alignment.BOTTOM_CENTER)
        if unit.position == "DEFAULT":
            stfed.services.blt.blt(default_placement_img, placement[0], placement[1], img, pal, side=side, alignment=stfed.services.blt.Alignment.BOTTOM_RIGHT)

    for space in mif.spaces:
        cel = None
        alignment = stfed.services.blt.Alignment.CENTER
           
        if space.preset_item is not None:
            cel = itemlib[stfed.model.ItemType(space.preset_item)]
        if space.pick_random_item is True:
            cel = random_item_on_raze_img
        if space.special_item_drop is True:
            cel = random_item_img
        if cel is None: 
            continue

        placement = (space.x_pos, space.y_pos)
        if placement == (0, 0) and len(space.placements) == 0:
            continue
        if placement == (0, 0):
            placement = space.placements[0]

        stfed.services.blt.blt(cel, placement[0], placement[1], img, pal, side=space.owner, alignment=alignment)
    random_item_img.close()
    random_item_on_raze_img.close()
    randunit_img.close()
    default_placement_img.close()

    hotspot_img =  PIL.Image.open("resources/hotspot.png")
    for s in mif.spaces:
        if s.hot_spot:
            for p in s.placements:
                stfed.services.blt.blt(hotspot_img, p[0], p[1], img, pal, alignment=stfed.services.blt.Alignment.CENTER)
    hotspot_img.close()

    bytes_io = io.BytesIO()
    img.save(bytes_io, format='PNG')
    content = bytes_io.getvalue()
    return content


def __find_default_placements(mif: stfed.model.MifMapInfoRes, tlb: stfed.model.TlbTileLibrary):
    result = {}
    import itertools
    all_units = [y for x in [[u]*u.count for u in mif.units] + [[u]*u.count for u in mif.rand_units]  for y in x]
    sorted_units = list(sorted(all_units, key=lambda u: u.owner.value))
    grouped = [(k, list(vs)) for k, vs in itertools.groupby(sorted_units, key=lambda u: u.owner.value)]
    for side_value, units in grouped:
        side = stfed.model.Side(side_value)
        startpoint = [
            (space.x_pos, space.y_pos)
            for space in mif.spaces
            if space.func_type == stfed.model.FuncType.FUNC_PORTAL
            if space.owner == side
        ]
        if len(startpoint) > 0:
            startpoint = startpoint[0]
        else:
            startpoint = [stfed.consts.WORLD_WIDTH // 2, stfed.consts.WORLD_HEIGHT // 2]
            # TODO: fix turtles

        subresult = []
        radius = 0
        perimeter = []
        for unit_idx in range(len(units)):
            while True:
                if len(perimeter) == 0:
                    radius = radius + 1
                    perimeter = [
                        p for p in 
                        (
                            [(startpoint[0] + dx, startpoint[1] - radius) for dx in range(-radius, radius + 1)]
                            + [(startpoint[0] + dx, startpoint[1] + radius) for dx in range(-radius, radius + 1)]
                            + [(startpoint[0] - radius, startpoint[1] + dy) for dy in range(-radius+1, radius)]
                            + [(startpoint[0] + radius, startpoint[1] + dy) for dy in range(-radius+1, radius)]
                        )
                        if 0 <= p[0] < stfed.consts.WORLD_WIDTH
                        if 0 <= p[1] < stfed.consts.WORLD_HEIGHT
                    ]
                maybe_pos = perimeter.pop()
                tile = mif.map_tiles[maybe_pos[0] + maybe_pos[1] * stfed.consts.WORLD_WIDTH]
                terrain =  tlb.tiles[tile].terrain_type
                can_place_here = (
                    not any(u.position == maybe_pos for u in mif.units + mif.rand_units)
                    and not any(any(p[:2] == maybe_pos for p in s.placements) for s in mif.spaces)
                    and terrain in walkable_terrain_types
                )
                if can_place_here:
                    subresult.append(maybe_pos)
                    break
        result[side] = list(reversed(subresult))
    return result