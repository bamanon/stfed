import dataclasses

@dataclasses.dataclass
class MapIdxRec:
    name: str
    esize: int
    num_recs: int
    num_chunks: int
    chunks_as_res: bool
    abbrev: bool
    patch: bool

    def map_filename(self):
        return f"{self.name.upper()}.MAP"


    def stf_filename(self):
        return f"{self.name.upper()}.STF"
