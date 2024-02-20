from fastapi import status

from src.core.common.exceptions import CustomHTTPException
from . import constants as config_enums

ConfigNotFound = CustomHTTPException(
    detail=config_enums.ConfigNotFound404DetailEnum.config,
    message=config_enums.ConfigNotFound404MessageEnum.config,
    status_code=status.HTTP_404_NOT_FOUND,
)

NoDocsInCollection = CustomHTTPException(
    detail=config_enums.ConfigNotFound404DetailEnum.no_docs,
    message=config_enums.ConfigNotFound404MessageEnum.no_docs,
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
