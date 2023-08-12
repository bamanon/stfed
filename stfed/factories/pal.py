import io

import PIL.Image

from stfed.model import Palette


PALETTE_LENGTH = 256


def parse(content: bytes) -> Palette:
    data = [
        (
            content[i * 3],
            content[i * 3 + 1],
            content[i * 3 + 2]
        )
        for i in range(PALETTE_LENGTH)
    ]
    return Palette(data)


def export_as_pcx(palette: Palette) -> bytes:
    image = PIL.Image.new('RGB', (PALETTE_LENGTH, 1), "black")
    for x in range(PALETTE_LENGTH):
        image.putpixel((x, 0), palette.data[x])
    bytes_io = io.BytesIO()
    image.save(bytes_io, format='PCX')
    content = bytes_io.getvalue()
    return content


def import_from_image(content: bytes) -> Palette:
    data = []
    image =  PIL.Image.open(io.BytesIO(content))
    pixels = image.load()
    for i in range(PALETTE_LENGTH):
         x = i % image.size[0]
         y = i // image.size[0]
         color = pixels.getpixel((x, y))
         data.append(color)
    return Palette(data)


def export_as_html(palette: Palette) -> str:
    COLUMN_COUNT = 16
    buf = "<table>\n"
    for row in range(len(palette.data) // COLUMN_COUNT):
        buf = buf + "\n<tr>"
        for col in range(COLUMN_COUNT):
            c = palette.data[COLUMN_COUNT * row + col]
            contr = (255 - c[0], 255 - c[1], 255 - c[2])
            background_color = f"rgb({c[0]}, {c[1]}, {c[2]})"
            foreground_color = f"rgb({contr[0]}, {contr[1]}, {contr[2]})"
            html_color = f"#{c[0]:02X}{c[1]:02X}{c[2]:02X}"
            buf = buf + f"<td style='line-height: 48px; padding: 4px; background-color: {background_color}; color: {foreground_color}'>{html_color}</td>"
        buf = buf + "</tr>"
    buf = buf + "</table>"
    return buf

