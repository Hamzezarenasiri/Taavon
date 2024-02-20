from fastapi import status

from src.core.common.exceptions import CustomHTTPException
from .constants import Organization422MessageEnum, Organization422DetailEnum
from .messages import OrganizationErrorMessageEnum, OrganizationNotFoundErrorDetailEnum

ParentOrganizationNotFound = CustomHTTPException(
    detail=OrganizationNotFoundErrorDetailEnum.parent_organization_not_found,
    message=OrganizationErrorMessageEnum.parent_organization_not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)
OrganizationNotFound = CustomHTTPException(
    detail=OrganizationNotFoundErrorDetailEnum.organization_not_found,
    message=OrganizationErrorMessageEnum.organization_not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)
CannotRecursiveOrganization = CustomHTTPException(
    message=Organization422MessageEnum.recursive,
    detail=Organization422DetailEnum.recursive,
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
)
