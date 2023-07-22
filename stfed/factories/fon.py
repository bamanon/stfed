import struct
import io

import PIL.Image

import stfed.model


def parse(resource: stfed.model.Resource) -> stfed.model.FontResource:
    data = resource.data()    
    font_header_format = "=8H"
    font_header_size = struct.calcsize(font_header_format)
    font_header_raw = struct.unpack_from(font_header_format, data)
    font_header = stfed.model.FontHeader(*font_header_raw)
    chars: list[stfed.model.FontArrayElement] = []
    char_header_format = "=HI"
    char_header_size = struct.calcsize(char_header_format)
    for i in range(resource.num_headers):
        char_header_raw = struct.unpack_from(char_header_format, data, font_header_size + i * char_header_size)
        char_header = stfed.model.FontCharHeader(*char_header_raw)
        char_start = font_header_size + resource.num_headers * char_header_size + char_header.offset
        char_data_size= font_header.height * char_header.char_wide
        char_data = data[char_start:char_start + char_data_size]
        char_element = stfed.model.FontArrayElement(char_header, char_data)
        chars.append(char_element)
    font_resource = stfed.model.FontResource(font_header, chars)
    return font_resource


def export_as_png(font_resource: stfed.model.FontResource, double_width: bool = False) -> bytes:
    unique_vals = list(set(sorted([
        p
        for c in font_resource.chars
        for p in c.char_data
    ])))
    highest_val = unique_vals[-1]
    step = 255 // highest_val
    COLCOUNT = 16
    max_height = font_resource.header.height
    # in 9.FON header.max_wide is 8 yet the widest char is 9
    max_width = max(c.char_header.char_wide for c in font_resource.chars)
    img = PIL.Image.new( 'RGBA', (max_width * 256 // COLCOUNT, max_height * COLCOUNT))
    img_pixels = img.load()
    for cy in range(256 // COLCOUNT):
        for cx in range(COLCOUNT):
            i = cx + cy * COLCOUNT
            if i < font_resource.header.first_char:
                continue
            if i >= len(font_resource.chars):
                break
            char_idx = i - font_resource.header.first_char
            char_element = font_resource.chars[char_idx]

            for dy in range(font_resource.header.height):
                for dx in range(char_element.char_header.char_wide):
                    v = char_element.char_data[dx + dy * char_element.char_header.char_wide]
                    color = (v * step, v * step, v * step)
                    if v == 0:
                        continue
                    img_pixels[cx * max_width + dx, cy * max_height + dy] = color
    if double_width:
        img = img.resize((img.width * 2, img.height))
    bytes_io = io.BytesIO()
    img.save(bytes_io, format='PNG')
    content = bytes_io.getvalue()
    return content
