import dataclasses

@dataclasses.dataclass
class MapRecord():
    resource_type: int
    resource_name: int
    num_offs: int
    offs_table: int
    