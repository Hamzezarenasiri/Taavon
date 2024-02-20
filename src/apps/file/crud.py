import os
from typing import Tuple

from src.core.base.crud import BaseCRUD
from . import schema as file_schema
from .models import File


class FileCRUD(BaseCRUD):
    async def save_file(self, file: file_schema.ValidatedFile, path: str) -> Tuple:
        file_name, file_extension = os.path.splitext(file.file_name)
        file_name_extention = file.file_name
        if not os.path.exists(path):
            os.makedirs(path)
        uploaded_file_path = f"{path}/{file.file_name}"
        counter = 1
        while os.path.exists(uploaded_file_path):
            file_name_extention = f"{file_name}_{counter}{file_extension}"
            counter += 1
            uploaded_file_path = f"{path}/{file_name_extention}"
        with open(f"{uploaded_file_path}", "wb+") as file_object:
            file_object.write(file.content)
        return file_name_extention, file.content_type


files_crud = FileCRUD(
    read_db_model=File,
    create_db_model=File,
    update_db_model=File,
)
