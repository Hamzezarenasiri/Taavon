import os
from io import BytesIO
from typing import Optional, Tuple

from PIL import Image, UnidentifiedImageError
from fastapi import BackgroundTasks

from src.core.common.enums import RoleEnum
from src.core.common.exceptions import UpdateFailed
from src.core.mixins import SchemaID, default_id
from src.core.video_process.video2gif import video_to_gif
from src.services.db.mongodb import UpdateOperatorsEnum
from . import schema as file_schema
from src.core.base.crud import BaseCRUD
from .constants import FileTypeEnum
from .exceptions import UnsupportedFileFormat
from .models import File
from ..user.models import User


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

    async def save_file_meta(
        self,
        file: file_schema.ValidatedFile,
        path: str,
        user_id: SchemaID,
        meta_fields: Optional[file_schema.FileUploadDataIn],
        file_id=None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> file_schema.FileCreateOut:
        original_file_path = f"{path}/original"
        file_name, file_type = await files_crud.save_file(
            file=file, path=original_file_path
        )
        _, file_extension = os.path.splitext(file.file_name)
        file_url = f"{original_file_path}/{file_name}"
        # file_out = await self.upload_file_to_public_s3(file, file_extension)
        thumbnail_path = f"{path}/thumbnail"
        thumbnail_ur = f"{thumbnail_path}/{file_name}"
        if not os.path.exists(thumbnail_path):
            os.makedirs(thumbnail_path)
        if FileTypeEnum.image.value in file_type:
            file_type = FileTypeEnum.image.value
            img = BytesIO(file.content)
            try:
                image: Image.Image = Image.open(img)
            except UnidentifiedImageError as e:
                raise UnsupportedFileFormat from e
            image.save(fp=thumbnail_ur, quality=100, optimize=True)
            # image.thumbnail((100, 100))
            img.seek(0)
            # thumb_file_out = await self.upload_thumbnail_to_public_s3(
            #     img, file_extension, file.content_type
            # )
            # thumbnail_ur = thumb_file_out.file_url
        elif FileTypeEnum.video.value in file_type:
            file_type = FileTypeEnum.video.value
            thumb_file_name = f"{os.path.splitext(file_name)[0]}.gif"
            thumbnail_ur = f"{thumbnail_path}/{thumb_file_name}"
            background_tasks.add_task(video_to_gif, file_url, thumbnail_ur)
        else:
            thumbnail_ur = ""
            file_type = FileTypeEnum.document.value

        meta_object = file_schema.FileCreateIn(
            file_type=file_type,
            file_name=file_name,
            thumbnail_url=thumbnail_ur,
            file_url=file_url,
            # file_category=meta_fields.file_category if meta_fields else None,
            alt=meta_fields.alt if meta_fields else None,
        )
        created = await files_crud.create(
            File(
                id=file_id or default_id(),
                **meta_object.dict(exclude_none=True),
                user_id=user_id,
            )
        )
        return file_schema.FileCreateOut(**created.dict())

    async def set_is_used(
        self, file_id: SchemaID, entity_id: SchemaID, current_user: User
    ) -> file_schema.FileUpdateOut:
        criteria = (
            {"id": file_id}
            if current_user.role == RoleEnum.ADMIN.value
            else {"id": file_id, "user_id": current_user.id}
        )
        updated, is_updated = await files_crud.update_and_get(
            criteria=criteria,
            new_doc={"entity_ids": entity_id},
            operator=UpdateOperatorsEnum.add_To_set_,
        )
        if not is_updated:
            raise UpdateFailed
        updated, is_updated = await files_crud.update_and_get(
            criteria=criteria,
            new_doc={"is_used": True},
        )
        if not is_updated:
            raise UpdateFailed
        return file_schema.FileUpdateOut(**updated.dict())


files_crud = FileCRUD(
    read_db_model=File,
    create_db_model=File,
    update_db_model=File,
)
