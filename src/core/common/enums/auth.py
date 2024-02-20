from enum import Enum


class RoleEnum(str, Enum):
    super_admin: str = "super_admin"
    admin: str = "admin"
    user: str = "user"


ALL_ROLES = [i.value for i in RoleEnum.__members__.values()]
