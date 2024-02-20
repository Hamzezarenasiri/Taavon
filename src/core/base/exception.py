from fastapi import status

from src.core.common.exceptions import CustomHTTPException

EntitiesNotFound = CustomHTTPException(
    detail=["entities_not_found"],
    message="Entities not found",
    status_code=status.HTTP_404_NOT_FOUND,
)
