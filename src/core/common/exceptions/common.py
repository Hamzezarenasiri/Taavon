from fastapi import status

from src.core.common.enums import (
    BadRequest400DetailEnum,
    BadRequest400MessageEnum,
    QueryParams422DetailEnum,
    QueryParams422MessageEnum,
    ServerError500DetailEnum,
    ServerError500MessageEnum,
    NotFound404MessageEnum,
    NotFound404DetailEnum,
)
from src.core.common.exceptions.base import CustomHTTPException

InternalServerError = CustomHTTPException(
    message=ServerError500MessageEnum.server_error,
    detail=ServerError500DetailEnum.server_error,
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)

DeleteFailed = CustomHTTPException(
    message=BadRequest400MessageEnum.delete_failed,
    detail=BadRequest400DetailEnum.delete_failed,
    status_code=status.HTTP_400_BAD_REQUEST,
)

UpdateFailed = CustomHTTPException(
    message=BadRequest400MessageEnum.update_failed,
    detail=BadRequest400DetailEnum.update_failed,
    status_code=status.HTTP_400_BAD_REQUEST,
)

InvalidQueryParams = CustomHTTPException(
    message=QueryParams422MessageEnum.invalid_query_params,
    detail=QueryParams422DetailEnum.invalid_query_params,
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
)
NotFound = CustomHTTPException(
    message=NotFound404MessageEnum.not_found,
    detail=NotFound404DetailEnum.not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)
