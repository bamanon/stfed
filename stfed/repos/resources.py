import io
import dataclasses
import os.path
import struct
import typing

import reactivex
import reactivex.operators

import stfed.model


_MAP_RECORD_PADDED_SIZE = 111


class ResourcesRepo:

    def __init__(self):
        self.__source_path = None
        self.__is_dirty = False
        self.__resources: typing.List[stfed.model.Resource] = []

        self.__is_dirty_subject = reactivex.subject.BehaviorSubject(self.__is_dirty)
        self.__source_path_subject = reactivex.subject.BehaviorSubject(self.__source_path)
        self.__resources_subject = reactivex.subject.BehaviorSubject(self.__resources)

    def initialize(self, source_path: str):
        if self.__is_other_map_file(source_path):
            map_file_paths = [source_path]
        elif self.__is_stf_file(source_path):
             map_file_paths = [source_path[:-3] + 'MAP']
        elif self.__is_directory(source_path):
            map_file_paths = [
                os.path.join(source_path, file_name)
                for file_name in os.listdir(source_path)
                if file_name.endswith('.MAP')
            ]
        # TODO: enable MAP.IDX/dir support once we sort out saving...
        # elif self.__is_map_idx_file(source_path):
        #     basedir = os.path.split(source_path)[0]
        #     map_file_paths = [
        #         os.path.join(basedir, r.map_filename())
        #         for r in self.__load_map_idx(source_path)
        #     ]

        else:
            raise Exception(f"Unsupported source: {source_path}")
        
        self.__resources = [
            resource
            for map_file_path in map_file_paths
            for resource in load_resources(map_file_path)
        ]
        self.__source_path = source_path
        self.__is_dirty = False
        self.__source_path_subject.on_next(self.__source_path)
        self.__is_dirty_subject.on_next(self.__is_dirty)
        self.__resources_subject.on_next(self.__resources)
        

    def get(
        self,
        rn: int,
        rt: stfed.model.ResourceType,
        source_file: typing.Optional[str] = None
    ) -> typing.Optional[stfed.model.Resource]:
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
    

    def is_dirty_o(self) -> reactivex.Observable[bool]:
        return self.__is_dirty_subject


    def all_resources_o(self) -> reactivex.Observable[typing.List[stfed.model.Resource]]:
        return self.__resources_subject
    
    def source_path_o(self) -> reactivex.Observable[typing.Optional[str]]:
        return self.__source_path_subject
    

    def get_o(
        self,
        rn: int,
        rt: stfed.model.ResourceType,
        source_file: typing.Optional[str] = None
    ) -> reactivex.Observable[typing.Optional[stfed.model.Resource]]:
        def pick(resources: typing.List[stfed.model.Resource]) -> typing.Optional[stfed.model.Resource]:
            matches = [
                r
                for r in resources
                if r.resource_name == rn
                and r.resource_type == rt.value
                and (source_file is None or r.source_file.endswith(source_file))
            ]
            if len(matches) == 0:
                return None
            return matches[0]
        return self.all_resources_o().pipe(reactivex.operators.map(pick))


    def all_resources(self):
        return self.__resources
    
    def is_dirty(self):
        return self.__is_dirty

    def source_path(self):
        return self.__source_path

    def update(self, resource: stfed.model.Resource):
        #TODO: read-only repos?
        resource = dataclasses.replace(resource, source_file=self.__source_path)
        index = -1
        for i, r in enumerate(self.__resources):
            if r.resource_name == resource.resource_name and r.resource_type == resource.resource_type:
                index = i
                break

        self.__resources = [r for r in self.__resources] #copy
        if index >= 0:
            self.__resources[index] = resource
        else:
            raise Exception(f"Trying to update a nonexistent {resource.resource_type.name} resource {resource.resource_name}")
            # self.__resources.append(resource)
        self.__is_dirty = True
        self.__is_dirty_subject.on_next(self.__is_dirty)
        self.__resources_subject.on_next(self.__resources)


    def delete(self, rn: int, rt: stfed.model.ResourceType):
        index = -1
        for i, r in enumerate(self.__resources):
            if r.resource_name == rn and r.resource_type == rt.value:
                index = i
                break
        if index < 0:
            raise Exception(f"Trying to delete a nonexistent {rt} resource {rn}")
            # return
        self.__resources = [r for i, r in enumerate(self.__resources) if i != index]
        self.__is_dirty = True
        self.__is_dirty_subject.on_next(self.__is_dirty)
        self.__resources_subject.on_next(self.__resources)


    def insert(self, resource: stfed.model.Resource):
        index = -1
        for i, r in enumerate(self.__resources):
            if r.resource_name == resource.resource_name and r.resource_type == resource.resource_type:
                index = i
                break
        if index >= 0:
            raise Exception(f"Trying to insert an existing {resource.resource_type.name} resource {resource.resource_name}")
        self.__resources = [r for r in self.__resources]
        self.__resources.append(resource)
        self.__is_dirty = True
        self.__is_dirty_subject.on_next(self.__is_dirty)
        self.__resources_subject.on_next(self.__resources)


    def commit(self, new_path: typing.Optional[str]=None):
        if self.__source_path is None:
            raise Exception("No file opened")
        elif not (self.__is_stf_file(self.__source_path) or self.__is_other_map_file(self.__source_path)):
            raise Exception("Unsupported scenario")
        if new_path is None and not self.__is_dirty:
            return
        if new_path is None:
            new_path = self.__source_path
        stf_path = new_path[:-3] + 'STF'
        map_path = new_path[:-3] + 'MAP'
        offset = 0
        if any(r.is_patch for r in self.__resources):
            raise Exception("PATCH-MAPs not supported")
        with open(map_path, 'wb') as map_f:
            for r in self.__resources:
                record_format = "=BIHI"
                record_size = struct.calcsize(record_format)
                packed = struct.pack(record_format, r.resource_type, r.resource_name, 1, offset)
                offset = offset + len(r.data()) + _extended_res_header_record_size #TODO: is_patch
                map_f.write(packed)
                map_f.write((_MAP_RECORD_PADDED_SIZE - record_size) * b'\x00')
        cached_data = [r.data() for r in self.__resources]
        with open(stf_path, 'wb') as stf_f:
            for i, r in enumerate(self.__resources):
                size = len(cached_data[i])
                res_header = stfed.model.ResHeader(
                    comp_type=0,
                    uncompressed_size=size,
                    size=size,
                    resource_type=r.resource_type,
                    num_headers=r.num_headers,
                    size_of_headers=r.size_of_headers,
                    data=b'\x00' * 6,
                    gen_id=0xfefe)
                stf_f.write(struct.pack(
                    _extended_res_header_record_format, #TODO: is_patch
                    r.resource_name,
                    *dataclasses.astuple(res_header)))
                stf_f.write(cached_data[i])
        self.__source_path = new_path
        self.initialize(self.__source_path)
        

    def __load_map_idx(self, map_idx_filepath: str) -> typing.List[stfed.model.MapIdxRec]:
        with open(map_idx_filepath, 'rb') as f:
            content = f.read()
        record_format = '=9sHHHBBB'
        record_lenght = struct.calcsize(record_format)
        raw_records = [content[i*record_lenght:(i+1)*record_lenght] for i in range(len(content)//record_lenght)]
        map_idx_records: typing.List[stfed.model.MapIdxRec] = []
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
    

def validate_res_header(path: str):
    with open(path, 'rb') as f:
        content = f.read()
    try:
        res_header = __read_res_header(content, 0, False)
    except:
        return (None, ["Resource header not found."])
    if (
        res_header.gen_id != 0xfefe
        or res_header.comp_type >= 127
        or res_header.num_headers >= 127
        or res_header.resource_type >= 64
        or res_header.size > len(content)
        or res_header.uncompressed_size > len(content)
    ):
        return (res_header, [f"Corrupted resource header: {res_header}."])
    return (res_header, [])


def load_single_resource_file_resource(
    path: str,
    is_headerless = False,
    rn: typing.Optional[int]=None,
    rt: typing.Optional[stfed.model.ResourceType] = None,
    num_headers: typing.Optional[int] = None,
    size_of_headers: typing.Optional[int] = None
) -> stfed.model.InMemoryResource:
    just_filename, ext = os.path.basename(path).split('.')
    with open(path, 'rb') as f:
        content = f.read()
    res_header = None
    if not is_headerless:
        res_header, errors = validate_res_header(path)
        if len(errors) > 0:
            raise Exception("Corrupted or missing header")

    rn = rn if rn is not None else int(just_filename)
    if rt is not None and res_header is not None and res_header.resource_type != rt.value:
        raise Exception(f"Non-matching resource type: expected {rt}, found: {res_header.resource_type}")
    if rt is None and res_header is not None:
        rt = res_header.resource_type
    if rt is None:
        rt = getattr(stfed.model.ResourceType, ext)
    if num_headers is None:
        num_headers = res_header.num_headers if res_header is not None else 0
    if size_of_headers is None:
        size_of_headers =  res_header.size_of_headers if res_header is not None else 0
    start = 0 if is_headerless else _res_header_record_size
    end = start + res_header.size if res_header is not None else -1
    data = content[start:end]
    resource = stfed.model.InMemoryResource(
        rn,
        rt.value,
        num_headers,
        size_of_headers,
        data,
        None,
        False)
    return resource


def save_single_file_resource(resource: stfed.model.Resource) -> bytes:
    with io.BytesIO() as f:
        data = resource.data()
        if not stfed.model.is_headerless(stfed.model.ResourceType(resource.resource_type)):
            size = len(data)
            res_header = stfed.model.ResHeader(
                comp_type=0,
                uncompressed_size=size,
                size=size,
                resource_type=resource.resource_type,
                num_headers=resource.num_headers,
                size_of_headers=resource.size_of_headers,
                data=b'\x00' * 6,
                gen_id=0xfefe)
            f.write(struct.pack(
                _res_header_record_format, #TODO: is_patch
                *dataclasses.astuple(res_header)))
        f.write(data)
        return f.getvalue()


def load_resources(path: str) -> typing.List[stfed.model.Resource]:
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
    map_records = __read_map_records(content, _MAP_RECORD_PADDED_SIZE)

    with open(stf_filepath, 'rb') as f:
        content = f.read()
    
    is_patch = len(content) == 0
    starts_with_rn = not is_patch
    if not is_patch:
        res_headers = [__read_res_header(content, mr.offs_table, starts_with_rn) for mr in map_records]
    else:
        res_headers = []
        for mr in map_records:
            mr.offs_table = 0
            external_resource_filename = f"{mr.resource_name}.{stfed.model.ResourceType(mr.resource_type).name}"
            external_resource_path = os.path.join(basedir, external_resource_filename)
            with open(external_resource_path, "rb") as f:
                content = f.read()
            res_header = __read_res_header(content, mr.offs_table, starts_with_rn)
            res_headers.append(res_header)

    resources = []
    for mr, rh in zip(map_records, res_headers):
        data_start = mr.offs_table + _res_header_record_size + (4 if starts_with_rn else 0)
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

_extended_res_header_record_format ="=IHIIHHH6sH"
_res_header_record_format = '=' + _extended_res_header_record_format[2:]

_res_header_record_size = struct.calcsize(_res_header_record_format)
_extended_res_header_record_size = struct.calcsize(_extended_res_header_record_format)


def __read_res_header(content: bytes, offs_table: int, starts_with_rn = True) -> stfed.model.ResHeader:
    start = offs_table + (4 if starts_with_rn else 0)
    end = start + _res_header_record_size
    record_raw = content[start:end]
    record = struct.unpack(_res_header_record_format, record_raw)
    res_header = stfed.model.ResHeader(*record)
    return res_header


def __read_map_records(content: bytes, padded_record_size: int, records_count: int = -1) -> typing.List[stfed.model.MapRecord]:
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
        self.__default_lookup_repos: typing.List[typing.Tuple[str, ResourcesRepo]] = []


    def set_primary_file_path(self, primary_file_path: str):
        self.__primary_repo.initialize(primary_file_path)


    def set_default_lookup_paths(self, default_lookup_paths: typing.List[str]):
        # TODO: additive loading maybe
        self.__default_lookup_repos.clear()
        for path in default_lookup_paths:
            repo = ResourcesRepo()
            repo.initialize(path)
            self.__default_lookup_repos.append((path, repo))


    def reset_paths(self):
        self.__primary_repo = ResourcesRepo()
        self.__default_lookup_repos = []


    def initialize(self, primary_file_path: str, default_lookup_paths: typing.List[str]):
        self.set_primary_file_path(primary_file_path)
        self.set_default_lookup_paths(default_lookup_paths)


    def get(
            self,
            rn: int,
            rt: stfed.model.ResourceType,
            source_file: typing.Optional[str] = None,
            look_in_default_lookup_paths: bool = True
    ) -> typing.Optional[stfed.model.Resource]:
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
    ) -> typing.List[stfed.model.Resource]:
        results = self.__primary_repo.all_resources()
        if look_in_default_lookup_paths:
            results = results + [
                resource
                for _, repo in self.__default_lookup_repos
                for resource in repo.all_resources()
            ]
        return results
    
    def update(self, resource: stfed.model.Resource):
        return self.__primary_repo.update(resource)
    
    def commit(self, new_path: typing.Optional[str] = None):
        self.__primary_repo.commit(new_path)
    
    def is_dirty(self) -> bool:
        return self.__primary_repo.is_dirty()
    
    def source_path(self):
        return self.__primary_repo.source_path()

    def is_dirty_o(self) -> reactivex.Observable[bool]:
        return self.__primary_repo.is_dirty_o()

    def all_resources_o(self) -> reactivex.Observable[typing.List[stfed.model.Resource]]:
        return self.__primary_repo.all_resources_o()
    
    def source_path_o(self) -> reactivex.Observable[typing.Optional[str]]:
        return self.__primary_repo.source_path_o()
        
    def get_o(
        self,
        rn: int,
        rt: stfed.model.ResourceType,
        source_file: typing.Optional[str] = None
    ) -> reactivex.Observable[typing.Optional[stfed.model.Resource]]:
        return self.__primary_repo.get_o(rn, rt, source_file)

resources_repo_instance = MultisourceRepo()

#11000120 your
#11000125 is ready
#11200027 warrior