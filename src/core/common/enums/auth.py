from enum import Enum


class RoleEnum(str, Enum):
    SUPER_ADMIN: str = "super_admin"
    ADMIN: str = "admin"
    VENDOR: str = "vendor"
    CUSTOMER: str = "customer"


ALL_ROLES = [i.value for i in RoleEnum.__members__.values()]
