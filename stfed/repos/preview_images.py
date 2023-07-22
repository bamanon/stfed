import tempfile
import shutil
import os

import stfed.model


class PreviewImagesRepo():

    def __init__(self):
        self.__dir = tempfile.mkdtemp()
        pass

    def get(self,
            source_file: str,
            resource_name: int,
            resource_type: stfed.model.ResourceType,
            index: int|None = None,
            tag: str|None = None
    ) -> bytes|None:
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
        index: int|None = None,
        tag: str|None = None
    ) -> None:
        filepath = self.__make_path(source_file, resource_name, resource_type, index, tag)
        with open(filepath, 'wb') as f:
            f.write(data)
        

    def invalidate(
        self,
        source_file: str,
        resource_name: int,
        resource_type: stfed.model.ResourceType,
        index: int|None = None,
        tag: str|None = None
    ) -> None:
        try:
            filepath = self.__make_path(source_file, resource_name, resource_type, index, tag)
            os.unlink(filepath)
        except:
            pass


    def __make_path(
        self,
        source_file: str,
        resource_name: int,
        resource_type: stfed.model.ResourceType,
        index: int|None = None,
        tag: str|None = None
    ) -> str:
        # TODO: handle two stf files with the same name in different directories
        source_file_part = os.path.split(source_file)[1].replace('.', '_')
        index_part = str(index) if index is not None else 0
        tag_part = ''
        if tag is not None:
            tag_part = f"_{tag}"
        return os.path.join(self.__dir, f"{source_file_part}_{resource_name}_{resource_type}_{index_part}_{tag_part}.png")    
    

    def __del__(self):
        shutil.rmtree(self.__dir)


preview_images_repo_instance = PreviewImagesRepo()