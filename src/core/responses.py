from .base.schema import ErrorResponse
from .common.enums.common_response import (
    Conflict409MessageEnum,
    FileSizeTooLarge413MessageEnum,
    Forbidden403MessageEnum,
    NotFound404MessageEnum,
    ServerError500MessageEnum,
    Unauthorized401MessageEnum,
)

common_responses = {
    401: {"model": ErrorResponse[Unauthorized401MessageEnum]},
    403: {"model": ErrorResponse[Forbidden403MessageEnum]},
    500: {"model": ErrorResponse[ServerError500MessageEnum]},
}
response_401 = {401: {"model": ErrorResponse[Unauthorized401MessageEnum]}}
response_403 = {403: {"model": ErrorResponse[Forbidden403MessageEnum]}}
response_404 = {404: {"model": ErrorResponse[NotFound404MessageEnum]}}
response_500 = {500: {"model": ErrorResponse[ServerError500MessageEnum]}}
response_409 = {409: {"model": ErrorResponse[Conflict409MessageEnum]}}
response_413 = {413: {"model": ErrorResponse[FileSizeTooLarge413MessageEnum]}}
