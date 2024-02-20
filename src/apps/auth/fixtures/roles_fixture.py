from src.apps.user.constants import DefaultRoleNameEnum
from .permissions_fixture import (
    admin_permissions,
    super_admin_permissions,
)

all_roles = {
    DefaultRoleNameEnum.super_admin: super_admin_permissions,
    DefaultRoleNameEnum.admin: admin_permissions,
}
