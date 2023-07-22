def display_hexdump(data: bytes) -> str:
    def to_visible(b: int) -> str:
        return chr(b) if 32 <= b < 127 else '.'
    buf = []
    i = 0
    while True:
        chunk = data[i*16 : (i+1)*16]
        addr = 16 * i
        first = ' '.join(f"{b:02x}" for b in chunk[:8]).ljust(23)
        second = ' '.join(f"{b:02x}" for b in chunk[8:]).ljust(23)
        encoded = ''.join(to_visible(b) for b in chunk)
        buf.append(f"{addr:08x}  {first}  {second}  |{encoded}|")
        if len(chunk) < 16:
            buf.append(f"{len(data):08x}")
            break
        i = i + 1
    return '\n'.join(buf)
