import typing

import PIL.Image

import stfed.model
import stfed.consts


import enum
class Alignment(enum.Enum):
    TOP_LEFT = enum.auto()
    CENTER = enum.auto()
    BOTTOM_CENTER = enum.auto()
    BOTTOM_RIGHT = enum.auto()


def blt_in_img_coords(
    src: typing.Union[stfed.model.CelResource, stfed.model.TlbTile, stfed.model.AniResource, PIL.Image.Image],
    x0: int,
    y0: int,
    dest: PIL.Image.Image,
    pal: stfed.model.Palette,
    transparent: bool = True,
    side: stfed.model.Side=stfed.model.Side.SIDE1
):
    if isinstance(src, stfed.model.AniResource):
        cel = src.cels[0]
        src_width = cel.header.width
        src_height = cel.header.height
        pixels = cel.data
    elif isinstance(src, stfed.model.CelResource):
        src_width = src.header.width
        src_height = src.header.height
        pixels = src.data
    elif isinstance(src, stfed.model.TlbTile):
        src_width = stfed.consts.TILE_WIDTH
        src_height = stfed.consts.TILE_HEIGHT
        pixels = src.bitmap
    elif isinstance(src, PIL.Image.Image):
        src_width, src_height = src.size
    else:
        raise Exception("Unsupported src type: " + type(src).__name__)
    
    #TODO: refactor away
    if isinstance(src, PIL.Image.Image):
        dest.paste(src, (x0, y0), mask=src if transparent else None)
        return

    for dy in range(src_height):
        for dx in range(src_width):
            x = x0 + dx
            y = y0 + dy
            pal_entry = pixels[dy * src_width + dx]
            if stfed.consts.UNIT_COLORS_START <= pal_entry < stfed.consts.UNIT_COLORS_END:
                if side == stfed.model.Side.SIDE2:
                    pal_entry = pal_entry + stfed.consts.UNIT_COLORS_LENGTH
                elif side == stfed.model.Side.HOSTILE or side == stfed.model.Side.NEUTRAL:
                    pal_entry = pal_entry - stfed.consts.UNIT_COLORS_START + stfed.consts.HOSTILE_COLORS_START
            if transparent and pal_entry == 254:
                continue
            color = pal.data[pal_entry]
            if 0 <= x < dest.size[0] and 0 <= y < dest.size[1]:
                dest.putpixel((x, y), color)
                


def blt_in_world_coords(
    src: typing.Union[stfed.model.CelResource, stfed.model.TlbTile, stfed.model.AniResource, PIL.Image.Image],
    world_x: int,
    world_y: int,
    dest: PIL.Image.Image,
    pal: stfed.model.Palette,
    transparent: bool = True,
    alignment: Alignment = Alignment.TOP_LEFT,
    side: stfed.model.Side=stfed.model.Side.NEUTRAL
):
    if isinstance(src, stfed.model.AniResource):
        cel = src.cels[0]
        src_width = cel.header.width
        src_height = cel.header.height
    elif isinstance(src, stfed.model.CelResource):
        src_width = src.header.width
        src_height = src.header.height
    elif isinstance(src, stfed.model.TlbTile):
        src_width = stfed.consts.TILE_WIDTH
        src_height = stfed.consts.TILE_HEIGHT
    elif isinstance(src, PIL.Image.Image):
        src_width, src_height = src.size
    else:
        raise Exception("Unsupported src type: " + type(src).__name__)
    
    if alignment == Alignment.TOP_LEFT:
        y0 = world_y * stfed.consts.TILE_HEIGHT
        x0 = world_x * stfed.consts.TILE_WIDTH 
    elif alignment == Alignment.BOTTOM_RIGHT:
        y0 = (world_y + 1) * stfed.consts.TILE_HEIGHT   - src_width
        x0 = (world_x + 1) * stfed.consts.TILE_WIDTH  - src_height
    elif alignment == Alignment.CENTER:
        y0 = int((world_y + 0.5) * stfed.consts.TILE_HEIGHT  - src_height /2)
        x0 = int((world_x + 0.5) * stfed.consts.TILE_WIDTH  - src_width /2)
    elif alignment == Alignment.BOTTOM_CENTER:
        y0 = int((world_y + 1) * stfed.consts.TILE_HEIGHT - src_height)
        x0 = int((world_x + 0.5) * stfed.consts.TILE_WIDTH  - src_width /2)
    else:
        raise Exception("Unsupported alignment: " + str(alignment))
    
    blt_in_img_coords(src, x0, y0, dest, pal, transparent, side)

    # #TODO: refactor away
    # if isinstance(src, PIL.Image.Image):
    #     dest.paste(src, (x0, y0), mask=src if transparent else None)
    #     return

    # for dy in range(src_height):
    #     for dx in range(src_width):
    #         x = x0 + dx
    #         y = y0 + dy
    #         pal_entry = pixels[dy * src_width + dx]
    #         if stfed.consts.UNIT_COLORS_START <= pal_entry < stfed.consts.UNIT_COLORS_END:
    #             if side == stfed.model.Side.SIDE2:
    #                 pal_entry = pal_entry + stfed.consts.UNIT_COLORS_LENGTH
    #             elif side == stfed.model.Side.HOSTILE or side == stfed.model.Side.NEUTRAL:
    #                 pal_entry = pal_entry - stfed.consts.UNIT_COLORS_START + stfed.consts.HOSTILE_COLORS_START
    #         if transparent and pal_entry == 254:
    #             continue
    #         color = pal.data[pal_entry]
    #         if 0 <= x < dest.size[0] and 0 <= y < dest.size[1]:
    #             dest.putpixel((x, y), color)
                
