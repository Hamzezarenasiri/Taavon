from typing import Optional

from src.core.base.controller import BaseController
from src.core.common.exceptions import UpdateFailed
from src.core.mixins import SchemaID
from . import schema as organization_schema
from .crud import organization_crud
from .exceptions import CannotRecursiveOrganization, ParentOrganizationNotFound
from .models import Organization
from ..common.constants import ConfirmStatusEnum
from ..user.models import User


class OrganizationController(BaseController):
    async def get_single_organization(
        self,
        target_organization_id: SchemaID,
        criteria: Optional[dict] = None,
    ) -> organization_schema.OrganizationGetOut:
        return await organization_crud.get_joined(
            target_id=target_organization_id,
            criteria=criteria,
        )

    async def update_single_organization(
        self,
        target_id: SchemaID,
        new_organization_data: organization_schema.OrganizationUpdateIn,
    ) -> organization_schema.OrganizationUpdateOut:
        target_organization = await organization_crud.get_by_id(
            _id=target_id,
        )
        new_organization_dict = new_organization_data.dict()
        ancestors = []
        if new_organization_data.parent:
            parent = await organization_crud.get_by_id(_id=new_organization_data.parent)
            ancestors = parent.ancestors
            if new_organization_data.parent == target_id or target_id in ancestors:
                raise CannotRecursiveOrganization
            ancestors.append(new_organization_data.parent)
            new_organization_dict.update(ancestors=ancestors)
        (
            updated_organization,
            is_updated,
        ) = await organization_crud.default_update_and_get(
            criteria=dict(id=target_id), new_doc=new_organization_dict
        )
        if not is_updated:
            raise UpdateFailed
        if updated_organization.parent != target_organization.parent:
            organization_crud.update_children_ancestors(target_organization, ancestors)
        updated_organization = await organization_crud.get_joined(
            target_id=target_id,
            criteria=dict(id=updated_organization.id),
        )
        return organization_schema.OrganizationUpdateOut(**updated_organization)

    async def create_new_obj(
        self, new_data: organization_schema.OrganizationCreateIn, **kwargs
    ) -> organization_schema.OrganizationCreateOut:
        ancestors = []
        if new_data.parent:
            parent = await organization_crud.get_by_id(
                _id=new_data.parent, raise_exception=False
            )
            if parent:
                ancestors.extend(parent.ancestors)
                ancestors.append(new_data.parent)
            else:
                raise ParentOrganizationNotFound
        return await self.crud.create(
            self.create_model(
                **new_data.dict(exclude_none=True), ancestors=ancestors, **kwargs
            )
        )

    async def confirm_obj(
        self, obj_id: SchemaID, status: ConfirmStatusEnum, current_user: User
    ):
        organization: Organization = await organization_crud.get_by_id(obj_id)
        updated_data = {
            "confirm_status": status,
        }
        new_doc = organization.copy(update=updated_data).dict()
        await self.crud.default_update(
            criteria={"_id": organization.id}, new_doc=new_doc
        )
        return await organization_crud.get_by_id(obj_id)


organization_controller = OrganizationController(
    crud=organization_crud,
)
