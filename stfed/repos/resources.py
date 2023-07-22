import os.path
import struct
import typing

import stfed.model



class ResourcesRepo:

    def __init__(self):
        self.__resources: list[stfed.model.Resource] = []

    def initialize(self, source_path: str):
        if self.__is_map_idx_file(source_path):
            basedir = os.path.split(source_path)[0]
            map_file_paths = [
                os.path.join(basedir, r.map_filename())
                for r in self.__load_map_idx(source_path)
            ]
        elif self.__is_other_map_file(source_path):
            map_file_paths = [source_path]
        elif self.__is_stf_file(source_path):
             map_file_paths = [source_path[:-3] + 'MAP']
        elif self.__is_directory(source_path):
            map_file_paths = [
                os.path.join(source_path, file_name)
                for file_name in os.listdir(source_path)
                if file_name.endswith('.MAP')
            ]
        else:
            raise Exception(f"Unsupported source: {source_path}")
        
        self.__resources = [
            resource
            for map_file_path in map_file_paths
            for resource in load_resources(map_file_path)
        ]


    def get(
            self,
            rn: int,
            rt: stfed.model.ResourceType,
            source_file: str|None = None
    ) -> stfed.model.Resource|None:
        matches = [
            r
            for r in self.__resources
            if r.resource_name == rn
            and r.resource_type == rt.value
            and (source_file is None or r.source_file.endswith(source_file))
        ]
        if len(matches) == 0:
            return None
        #elif len(matches > 1): # prioritization?
        return matches[0]
    

    def all_resources(self):
        return self.__resources


    def __load_map_idx(self, map_idx_filepath: str) -> list[stfed.model.MapIdxRec]:
        with open(map_idx_filepath, 'rb') as f:
            content = f.read()
        record_format = '=9sHHHBBB'
        record_lenght = struct.calcsize(record_format)
        raw_records = [content[i*record_lenght:(i+1)*record_lenght] for i in range(len(content)//record_lenght)]
        map_idx_records: list[stfed.model.MapIdxRec] = []
        for raw_record in raw_records:
            name, esize, num_rects, num_chunks, chunks_as_res, abbrev, patch = struct.unpack(record_format, raw_record)
            name = name.decode('ascii').strip('\x00')
            chunks_as_res = bool(chunks_as_res)
            abbrev = bool(abbrev)
            patch = bool(patch)
            map_idx_records.append(
                stfed.model.MapIdxRec(name, esize, num_rects, num_chunks, chunks_as_res, abbrev, patch))
        return map_idx_records
    

    def __is_map_idx_file(self, source_path: str) -> bool:
        return os.path.split(source_path)[1] == "MAP.IDX"


    def __is_other_map_file(self, source_path: str) -> bool:
        return os.path.split(source_path)[1].endswith(".MAP")

    def __is_stf_file(self, source_path: str) -> bool:
        return os.path.split(source_path)[1].endswith(".STF")


    def __is_directory(self, source_path: str) -> bool:
        return os.path.isdir(source_path)
    
    
def load_resources(path: str) -> list[stfed.model.Resource]:
    basedir, filename = os.path.split(path)
    if '.' not in filename:
        raise Exception("Dirs not supported yet")
    if path.endswith('IDX'):
        raise Exception("IDX not supported yet")
        
    map_filepath = path[:-3] + 'MAP'
    stf_filepath = path[:-3] + 'STF'
    stf_filename = os.path.split(stf_filepath)[1]

    with open(map_filepath, 'rb') as f:
        content = f.read()
    map_records = __read_map_records(content, 111)

    with open(stf_filepath, 'rb') as f:
        content = f.read()
    
    is_patch = len(content) == 0
    if not is_patch:
        res_headers = [__read_res_header(content, mr, is_patch) for mr in map_records]
    else:
        res_headers = []
        for mr in map_records:
            mr.offs_table = 0
            external_resource_filename = f"{mr.resource_name}.{stfed.model.ResourceType(mr.resource_type).name}"
            external_resource_path = os.path.join(basedir, external_resource_filename)
            with open(external_resource_path, "rb") as f:
                content = f.read()
            res_header = __read_res_header(content, mr, is_patch)
            res_headers.append(res_header)

    resources = []
    for mr, rh in zip(map_records, res_headers):
        data_start = mr.offs_table + _res_header_record_size + (0 if is_patch else 4)
        size_to_use = rh.size if rh.size > 0 else rh.uncompressed_size
        resource = stfed.model.Resource(
            stf_filepath,
            mr.resource_name,
            mr.resource_type,
            data_start,
            size_to_use,
            rh.num_headers,
            rh.size_of_headers,
            is_patch
        )
        resources.append(resource)
    return resources


_res_header_record_format = "=HIIHHH6sH"
_res_header_record_size = struct.calcsize(_res_header_record_format)

def __read_res_header(content: bytes, map_record: stfed.model.MapRecord, is_patch = False) -> stfed.model.ResHeader:
    start = map_record.offs_table + (0 if is_patch else 4)
    end = start + _res_header_record_size
    record_raw = content[start:end]
    record = struct.unpack(_res_header_record_format, record_raw)
    res_header = stfed.model.ResHeader(*record)
    return res_header


def __read_map_records(content: bytes, padded_record_size: int, records_count: int = -1) -> list[stfed.model.MapRecord]:
    _map_record_format = "=BIHI"
    _map_record_size = struct.calcsize(_map_record_format)    
    map_records = []
    rest = content
    while len(rest) > 0 or len(map_records) == records_count:
        raw_record, rest = rest[:padded_record_size], rest[padded_record_size:]
        rt, rn, num_offs, offs_table = struct.unpack(_map_record_format, raw_record[:_map_record_size])
        map_record = stfed.model.MapRecord(rt, rn, num_offs, offs_table)
        map_records.append(map_record)
    return map_records


class MultisourceRepo():
    # TODO: merge with ResourcesRepo impl
    def __init__(self):
        self.__primary_repo = ResourcesRepo()
        self.__default_lookup_repos: list[typing.Tuple[str, ResourcesRepo]] = []


    def set_primary_file_path(self, primary_file_path: str):
        self.__primary_repo.initialize(primary_file_path)


    def set_default_lookup_paths(self, default_lookup_paths: list[str]):
        # TODO: additive loading maybe
        self.__default_lookup_repos.clear()
        for path in default_lookup_paths:
            repo = ResourcesRepo()
            repo.initialize(path)
            self.__default_lookup_repos.append((path, repo))


    def reset_paths(self):
        self.__primary_repo = ResourcesRepo()
        self.__default_lookup_repos = []


    def initialize(self, primary_file_path: str, default_lookup_paths: list[str]):
        self.set_primary_file_path(primary_file_path)
        self.set_default_lookup_paths(default_lookup_paths)


    def get(
            self,
            rn: int,
            rt: stfed.model.ResourceType,
            source_file: str|None = None,
            look_in_default_lookup_paths: bool = True
    ) -> stfed.model.Resource|None:
        result = self.__primary_repo.get(rn, rt, source_file)
        if result is not None or look_in_default_lookup_paths is False:
            return result
        for _, repo in self.__default_lookup_repos:
            result = repo.get(rn, rt, source_file)
            if result is not None:
                return result
        return None
        

    def all_resources(
            self,
            look_in_default_lookup_paths: bool = False
    ) -> list[stfed.model.Resource]:
        results = self.__primary_repo.all_resources()
        if look_in_default_lookup_paths:
            results = results + [
                resource
                for _, repo in self.__default_lookup_repos
                for resource in repo.all_resources()
            ]
        return results
    
resources_repo_instance = MultisourceRepo()
