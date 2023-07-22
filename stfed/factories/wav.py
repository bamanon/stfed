import io
import math
import wave

import PIL.Image
            

def export_preview(content: bytes) -> bytes:
    #TODO: make customizable
    IMAGE_HEIGHT = 256
    IMAGE_WIDTH = 512
    PIXELS_PER_SEC = None # mutually exclusive w IMAGE_WIDTH
    BACKGROUND_COLOR = (127, 127, 127)
    FOREGROUND_COLOR = (0, 0, 80)
    with io.BytesIO(content) as f, wave.open(f) as wave_read:
        frames = wave_read.readframes(wave_read.getnframes())
        framerate = wave_read.getframerate()
        if IMAGE_WIDTH is None:
            pixelscount = int(math.ceil(len(frames) * PIXELS_PER_SEC / framerate))
        else:
            pixelscount = IMAGE_WIDTH
        min_val = min(frames)
        max_val = max(frames)
        the_range = max_val - min_val
        if the_range == 0:
            min_val = -127
            the_range = 256
        image = PIL.Image.new('RGB', (pixelscount, IMAGE_HEIGHT), BACKGROUND_COLOR)
        for i in range(pixelscount):
            step = len(frames) // pixelscount
            start = i * step
            end = (i + 1) * step
            fragment = frames[start:end]
            min_in_frag = min(fragment)
            max_in_frag = max(fragment)
            min_scaled = (min_in_frag - min_val) * IMAGE_HEIGHT // the_range
            max_scaled = (max_in_frag - min_val) * IMAGE_HEIGHT // the_range
            if max_scaled == min_scaled:
                if max_scaled + 1 < IMAGE_HEIGHT:
                    max_scaled = max_scaled + 1
                else:
                    min_scaled = min_scaled - 1
            for y in range(min_scaled, max_scaled):
                image.putpixel((i, y), FOREGROUND_COLOR)
    bytes_io = io.BytesIO()
    image.save(bytes_io, format='PNG')
    result = bytes_io.getvalue()
    return result