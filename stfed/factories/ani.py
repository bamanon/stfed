import io
import math
import struct
import typing

import PIL.Image

import stfed.model


def parse(resource: stfed.model.Resource) -> stfed.model.AniResource:
    content = resource.data()

    record_format = '=iiHHHI'
    record_lenght = struct.calcsize(record_format)
    cel_resources : typing.List[stfed.model.CelResource] = []
    for i in range(resource.num_headers):
        raw = content[i * record_lenght:(i + 1)*record_lenght]
        if len(raw) < 18:
            raise Exception("Unable to parse resource; Corrupted CelHeader encountered")
        cel_header = stfed.model.CelHeader(*struct.unpack(record_format, raw))
        start = resource.size_of_headers +   cel_header.offset 
        end = start + cel_header.height * cel_header.width
        pixeldata = content[start:end]
        cel_resource = stfed.model.CelResource(cel_header, pixeldata)
        cel_resources.append(cel_resource)
    ani_resource = stfed.model.AniResource(cel_resources)
    return ani_resource


def export_image(
    cel: stfed.model.CelResource,
    pal: stfed.model.Palette,
    side: stfed.model.Side=stfed.model.Side.SIDE1
) -> bytes:
    width = cel.header.width
    height = cel.header.height
    # workaround for 2525.ANI having 0x65536
    dest_width = width if width > 0 and height > 0 else 1
    dest_height = height  if width > 0 and height > 0 else 1
    img = PIL.Image.new( 'RGB', (dest_width, dest_height), "black")
    stfed.services.blt.blt_in_img_coords(cel, 0, 0, img, pal, side=side, transparent=False)
    bytes_io = io.BytesIO()
    img.save(bytes_io, format='PNG')
    content = bytes_io.getvalue()
    return content


def export_spritemap(
    ani: stfed.model.AniResource,
    pal: stfed.model.Palette,
    double_width: bool
) -> bytes:
    max_cel_width = max(cel.header.width for cel in ani.cels)
    max_cel_height = max(cel.header.height for cel in ani.cels)
    col_count = math.ceil(math.sqrt(len(ani.cels)))
    row_count = math.ceil(len(ani.cels) / col_count)
    image_width = max(col_count * max_cel_width, 1)
    image_height = max(row_count * max_cel_height, 1)
    img = PIL.Image.new( 'RGBA', (image_width, image_height))
    for i, cel in enumerate(ani.cels):
        row = i // col_count
        col = i % col_count
        x0 = col * max_cel_width
        y0 = row * max_cel_height
        stfed.services.blt.blt_in_img_coords(cel, x0, y0, img, pal, transparent=False)
    if double_width:
        img = img.resize((img.width * 2, img.height))
    bytes_io = io.BytesIO()
    img.save(bytes_io, format='PNG')
    content = bytes_io.getvalue()
    return content
