from typing import Optional

from src.core.base.field import PasswordField, UsernameField
from src.core.base.schema import BaseSchema
from src.core.mixins import UsernameModel


class UsernamePasswordSchema(BaseSchema):
    username: UsernameField
    password: Optional[PasswordField]
