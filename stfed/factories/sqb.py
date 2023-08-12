import io
import json
import typing 

import stfed.model


def parse(resource: stfed.model.Resource) -> stfed.model.SquibResource:
    content = resource.data()
    squib_count = int.from_bytes(content[:4], 'little')
    squibs:typing.Dict[int, str] = {}
    headers_start = 4
    for i in range(squib_count):
        start = headers_start + i*8
        offset = int.from_bytes(content[start : start+4], 'little', signed=True)
        squib_id = int.from_bytes(content[start+4 : start+8], 'little', signed=True)
        start = headers_start + 8*squib_count + offset
        end = content.find(b'\x00', start)
        text = content[start:end].decode('cp437')
        squibs[squib_id] = text
    resource = stfed.model.SquibResource(resource.resource_name, squibs)
    return resource


def dump(model: stfed.model.SquibResource) -> bytes:
    ordered_squibs = list(sorted([(key, text) for key, text in model.squibs.items()], key=lambda t: t[0]))
    with io.BytesIO() as f:
        f.write(len(model.squibs).to_bytes(4, 'little'))
        #offset = 4 + 8 * len(ordered_squibs)
        offset = 0
        for key, text in ordered_squibs:
            f.write(offset.to_bytes(4, 'little'))
            f.write(key.to_bytes(4, 'little'))
            encoded_text = text.encode('cp437') + b'\x00'
            offset = offset + len(encoded_text) # +1?
        for _, text in ordered_squibs:
            encoded_text = text.encode('cp437') + b'\x00'
            f.write(encoded_text)
        f.seek(0)
        result = f.read()
    return result


def export_as_json(resource: stfed.model.Resource) -> str:
    return export_multiple_as_json([resource])


def export_multiple_as_json(resources: typing.List[stfed.model.Resource]) -> str:
    wrapped = [parse(r) for r in resources]
    list_of_dicts = [
        {
            "rn": wrapper.resource_name,
            "id": key,
            "text": squib,
        }
        for wrapper in wrapped
        for key, squib in sorted(wrapper.squibs.items(), key=lambda t: t[0])
    ]
    content = json.dumps(list_of_dicts, indent=4)
    return content


def import_json(content: str) -> typing.List[stfed.model.SquibResource]:
    list_of_dicts: typing.List[typing.Dict[str, any]] = json.loads(content)
    import itertools
    grouped = itertools.groupby(
        sorted(list_of_dicts, key=lambda d: d['rn']),
        key=lambda d: d['rn'])
    instantiated = [
        (rn, list(sorted(vs, key=lambda d: d['id'])))
        for rn, vs in grouped
    ]
    result = [
        stfed.model.SquibResource(
            rn,
            {d['id']: d['text'] for d in ds}
        )
        for rn, ds in instantiated
    ]
    return result
