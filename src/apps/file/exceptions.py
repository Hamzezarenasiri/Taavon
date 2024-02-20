from fastapi import status

from src.core.common.exceptions import CustomHTTPException
from .constants import (
    FileIsUsedMessageEnum,
    FileSize413MessageEnum,
    FileType415MessageEnum,
    S3ServiceUnavailableMessageEnum,
)

FileSizeTooLarge = CustomHTTPException(
    message=FileSize413MessageEnum.too_large,
    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
)

UnsupportedFileFormat = CustomHTTPException(
    message=FileType415MessageEnum.file_type,
    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
)

S3ServiceUnavailable = CustomHTTPException(
    message=S3ServiceUnavailableMessageEnum.service_unavailable,
    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
)

S3FileNotFound = CustomHTTPException(
    message=S3ServiceUnavailableMessageEnum.file_not_found,
    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
)

FileIsUsed = CustomHTTPException(
    message=FileIsUsedMessageEnum.file_is_used,
    status_code=status.HTTP_400_BAD_REQUEST,
)
