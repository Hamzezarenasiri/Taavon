from src.apps.user.constants import DefaultRoleNameEnum
from .permissions_fixture import (
    admin_permissions,
    super_admin_permissions,
)

all_roles = {
    DefaultRoleNameEnum.SUPER_ADMIN: super_admin_permissions,
    DefaultRoleNameEnum.ADMIN: admin_permissions,
}
