import tempfile
import shutil
import os
import typing

import stfed.model


class PreviewImagesRepo():

    def __init__(self):
        self.__dir = tempfile.mkdtemp()
        pass

    def get(self,
            source_file: str,
            resource_name: int,
            resource_type: stfed.model.ResourceType,
            index: typing.Optional[int] = None,
            tag: typing.Optional[str] = None
    ) -> typing.Optional[bytes]:
        filepath = self.__make_path(source_file, resource_name, resource_type, index, tag)
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except:
            return None
        

    def put(
        self,
        source_file: str,
        resource_name: int,
        resource_type: stfed.model.ResourceType,
        data: bytes,
        index: typing.Optional[int] = None,
        tag: typing.Optional[str] = None
    ) -> None:
        filepath = self.__make_path(source_file, resource_name, resource_type, index, tag)
        with open(filepath, 'wb') as f:
            f.write(data)
        

    def invalidate(
        self,
        source_file: str,
        resource_name: int,
        resource_type: stfed.model.ResourceType,
        index: typing.Optional[int] = None,
        tag: typing.Optional[str] = None
    ) -> None:
        try:
            filepath = self.__make_path(source_file, resource_name, resource_type, index, tag)
            os.unlink(filepath)
        except:
            pass

    def invalidate_matching(
        self,
        source_file: str,
        resource_name: int,
        resource_type: stfed.model.ResourceType,
    ) -> None:
        mask = self.__make_partial_path(source_file, resource_name, resource_type)
        for filename in os.listdir(self.__dir):
            filepath = os.path.join(self.__dir, filename)
            if filepath.startswith(mask):
                try:
                    os.unlink(filepath)
                except:
                    pass


    def invalidate_all(self):
        for filename in os.listdir(self.__dir):
            try:
                os.unlink(os.path.join(self.__dir, filename))
            except:
                pass


    def __make_path(
        self,
        source_file: str,
        resource_name: int,
        resource_type: stfed.model.ResourceType,
        index: typing.Optional[int] = None,
        tag: typing.Optional[str] = None
    ) -> str:
        # TODO: handle two stf files with the same name in different directories
        source_file_part = os.path.split(source_file)[1].replace('.', '_')
        index_part = ''
        if index is not None:
            index_part = f"_{index}" 
        tag_part = ''
        if tag is not None:
            tag_part = f"_{tag}"
        return os.path.join(self.__dir, f"{source_file_part}_{resource_name}_{resource_type.name}{index_part}{tag_part}.png")    
    
    
    def __make_partial_path(
        self,
        source_file: str,
        resource_name: int,
        resource_type: stfed.model.ResourceType,
    ) -> str:
        return self.__make_path(source_file, resource_name, resource_type, None, None)[:-4]
    


    def __del__(self):
        shutil.rmtree(self.__dir)


preview_images_repo_instance = PreviewImagesRepo()