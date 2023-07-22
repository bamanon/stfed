import dataclasses


@dataclasses.dataclass
class ResHeader():
    #resource_name: int
    comp_type: int
    uncompressed_size: int
    size: int
    resource_type: int
    num_headers: int
    size_of_headers: int
    data: bytes
    gen_id: int