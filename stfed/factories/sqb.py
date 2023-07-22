import stfed.model

def parse(content: bytes) -> stfed.model.SquibResource:
    squib_count = int.from_bytes(content[:4], 'little')
    squibs: dict[int, str] = {}
    headers_start = 4
    for i in range(squib_count):
        start = headers_start + i*8
        offset = int.from_bytes(content[start : start+4], 'little', signed=True)
        squib_id = int.from_bytes(content[start+4 : start+8], 'little', signed=True)
        start = headers_start + 8*squib_count + offset
        end = content.find(b'\x00', start)
        text = content[start:end].decode('cp437')
        squibs[squib_id] = text
    resource = stfed.model.SquibResource(squibs)
    return resource
