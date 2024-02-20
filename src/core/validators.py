import os

import magic
from fastapi import File, UploadFile

from src.apps.file.exceptions import FileSizeTooLarge, UnsupportedFileFormat
from src.apps.file.schema import ValidatedFile
from src.main.config import app_settings


async def file_validation(_file: UploadFile = File(...)) -> ValidatedFile:
    if (
        os.stat(_file.file.fileno()).st_size
        > app_settings.REQUEST_ATTACHMENT_MAX_FILE_SIZE
    ):
        raise FileSizeTooLarge

    content = _file.file.read()
    if (
        magic.from_buffer(content, mime=True)
        not in app_settings.REQUEST_ATTACHMENT_SUPPORTED_FORMATS
    ):
        raise UnsupportedFileFormat

    return ValidatedFile(
        content=content, file_name=_file.filename, content_type=_file.content_type
    )


async def avatar_validation(avatar: UploadFile = File(...)) -> ValidatedFile:
    if os.stat(avatar.file.fileno()).st_size > app_settings.USER_AVATAR_MAX_FILE_SIZE:
        raise FileSizeTooLarge

    content = avatar.file.read()
    if (
        magic.from_buffer(content, mime=True)
        not in app_settings.USER_AVATAR_SUPPORTED_FORMATS
    ):
        raise UnsupportedFileFormat

    return ValidatedFile(
        content=content, file_name=avatar.filename, content_type=avatar.content_type
    )
