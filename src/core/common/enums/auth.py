from enum import Enum


class RoleEnum(str, Enum):
    super_admin: str = "راهبر اصلی"
    admin: str = "راهبر فنی"
    user: str = "user"


ALL_ROLES = [i.value for i in RoleEnum.__members__.values()]
