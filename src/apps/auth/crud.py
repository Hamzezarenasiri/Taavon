from typing import List, Optional, Union, Any

from fastapi.security import SecurityScopes

from src.apps.auth.exceptions import PermissionDenied
from src.apps.auth.models import (
    Entity,
    Role,
)
from src.apps.user.constants import DefaultRoleNameEnum
from src.apps.user.models import User
from src.core.base.crud import BaseCRUD


class RoleCRUD(BaseCRUD):
    async def get_list_by_names(
        self,
        names: Optional[List[Union[str, DefaultRoleNameEnum]]],
        skip: int = 0,
        limit: Optional[int] = None,
        sort: Optional[Any] = None,
        deleted: Optional[bool] = None,
    ) -> Optional[List[Role]]:
        return (
            await self.get_list(
                criteria={"name": {"$in": names}},
                skip=skip,
                limit=limit,
                sort=sort,
                deleted=deleted,
            )
            if names
            else None
        )


class EntityCRUD(BaseCRUD):
    async def get_entity_rules(self, code_name: str) -> List[str]:
        entities = await self.get_object(criteria={"code_name": code_name})
        return entities.rules

    async def get_all_entities_name(self) -> List[str]:
        permissions = await self.get_list()
        return [entity.code_name for entity in permissions]


class PermissionCRUD(object):
    async def get_permissions_dict(self, user_obj: User) -> dict:
        roles = await roles_crud.get_list_by_names(names=user_obj.roles) or []
        permissions = {
            permission.entity: permission.rules
            for permission in user_obj.permissions or []
        }
        for role in roles:
            for permission in role.permissions:
                if permissions.get(permission.entity):
                    permissions[permission.entity] = list(
                        set(permission.rules + permissions[permission.entity])
                    )
                permissions[permission.entity] = permission.rules
        return permissions

    async def check_permissions(
        self, security_scopes: SecurityScopes, user_obj: User
    ) -> User:
        if not security_scopes.scopes:
            return user_obj
        entity_scope, rule = security_scopes.scopes
        permissions = await self.get_permissions_dict(user_obj)
        if entity_scope in permissions and rule in permissions[entity_scope]:
            return user_obj
        else:
            raise PermissionDenied


entities_crud = EntityCRUD(
    read_db_model=Entity,
    create_db_model=Entity,
    update_db_model=Entity,
)

roles_crud = RoleCRUD(
    read_db_model=Role,
    create_db_model=Role,
    update_db_model=Role,
)

permissions_crud = PermissionCRUD()
