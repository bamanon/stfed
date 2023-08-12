import dataclasses
import enum
import os.path
import typing


class ResourceType(enum.Enum):
    CEL = 0
    ANI = 1
    PIC = 2
    HMP = 3
    WAV = 4
    PAL = 5
    DAT = 6
    FON = 7
    SQB = 8
    CNV = 9
    DCL = 10
    CGF = 11
    BNK = 12
    SYN = 13
    CHU = 14
    ROT = 15
    SAV = 16
    FLC = 17
    TLB = 18
    MIF = 19
    STF = 20
    _8TR = 21
    SMK = 22
    SCR = 23
    _UNKOWN = 127


def is_headerless(rt: ResourceType):
    return rt in [
        ResourceType.WAV, ResourceType.HMP, ResourceType.BNK,
        ResourceType.SYN, ResourceType.SAV, ResourceType.FLC,
        ResourceType._8TR, ResourceType.SMK, ResourceType.SCR,
    ]


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


@dataclasses.dataclass
class Resource:
    source_file: str
    resource_name: int
    resource_type: int
    data_offset: int
    data_lenght: int
    num_headers: int
    size_of_headers: int
    is_patch: bool

    def data(self) -> bytes:
        if self.is_patch:
            actual_source_file = os.path.join(
                os.path.split(self.source_file)[0],
                self.label())
        else:
            actual_source_file = self.source_file
        with open(actual_source_file, 'rb') as f:
            f.seek(self.data_offset)
            data = f.read(self.data_lenght + self.size_of_headers)
        return data
    

    def source_filename(self) -> str:
        return os.path.split(self.source_file)[1]
    
    def extension(self):
        try:
            mapped = ResourceType(self.resource_type)
            if mapped == ResourceType._8TR.name:
                return "8TR"
            else:
                return mapped.name
        except:
           return '???'
        
    def label(self):
        return f"{self.resource_name}.{self.extension()}"


@dataclasses.dataclass
class InMemoryResource():
    resource_name: int
    resource_type: int
    num_headers: int
    size_of_headers: int
    data_: bytes
    source_file: typing.Optional[str] = None
    is_patch: bool = False

    @property
    def data_offset(self):
        return -1
    
    @property
    def data_lenght(self):
        return len(self.data_)

    def data(self) -> bytes:
        return self.data_

    def source_filename(self) -> str:
        return os.path.split(self.source_file)[1]
    
    def extension(self):
        try:
            mapped = ResourceType(self.resource_type)
            if mapped == ResourceType._8TR.name:
                return "8TR"
            else:
                return mapped.name
        except:
           return '???'
        
    def label(self):
        return f"{self.resource_name}.{self.extension()}"

