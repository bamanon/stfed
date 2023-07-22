import os.path
import dataclasses

from stfed.model.ResourceType import ResourceType


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

