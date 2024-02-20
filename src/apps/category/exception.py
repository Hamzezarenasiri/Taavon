from fastapi import status

from src.apps.category.constants import (
    CategoryNotFoundErrorDetailEnum,
    Category422MessageEnum,
    Category422DetailEnum,
    CategoryNotFoundErrorMessageEnum,
    CategoryErrorDetailEnum,
    CategoryErrorMessageEnum,
)
from src.core.common.exceptions import CustomHTTPException

CannotRecursiveCategory = CustomHTTPException(
    message=Category422MessageEnum.recursive,
    detail=Category422DetailEnum.recursive,
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
)

CategoryNotFound = CustomHTTPException(
    detail=CategoryNotFoundErrorDetailEnum.not_found,
    message=CategoryNotFoundErrorMessageEnum.not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)

CategoryHasChild = CustomHTTPException(
    detail=Category422DetailEnum.has_child,
    message=Category422MessageEnum.has_child,
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
)

CategoriesHaveChild = CustomHTTPException(
    detail=CategoryErrorDetailEnum.have_child,
    message=CategoryErrorMessageEnum.have_child,
    status_code=status.HTTP_400_BAD_REQUEST,
)
CategoryHasProduct = CustomHTTPException(
    detail=Category422DetailEnum.has_product,
    message=Category422MessageEnum.has_product,
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
)

CategoriesHaveProduct = CustomHTTPException(
    detail=CategoryErrorDetailEnum.have_product,
    message=CategoryErrorMessageEnum.have_product,
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
)
