import io
import struct

import PIL.Image

import stfed.model


def parse(resource: stfed.model.Resource) -> stfed.model.AniResource:
    content = resource.data()

    record_format = '=iiHHHI'
    record_lenght = struct.calcsize(record_format)
    cel_resources : list[stfed.model.CelResource] = []
    for i in range(resource.num_headers):
        raw = content[i * record_lenght:(i + 1)*record_lenght]
        if len(raw) < 18:
            raise Exception("Unable to parse resource; Corrupted CelHeader encountered")
        cel_header = stfed.model.CelHeader(*struct.unpack(record_format, raw))
        # if cel_header.height == 0 or cel_header.width == 0:
        #     continue
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
    stfed.services.blt.blt(cel, 0, 0, img, pal, side=side, transparent=False)
    bytes_io = io.BytesIO()
    img.save(bytes_io, format='PNG')
    content = bytes_io.getvalue()
    return content
