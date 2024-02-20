from typing import Dict, Optional

from src.apps.language.constants import LanguageEnum, LocaleEnum
from src.core.base.schema import BaseSchema


class LanguageListOut(BaseSchema):
    name: str
    code: LanguageEnum
    icon: Optional[str]
    direction: Optional[str]
    locale: LocaleEnum
    is_default: bool


class LanguageGetOut(BaseSchema):
    name: str
    code: LanguageEnum
    icon: Optional[str]
    direction: Optional[str]
    locale: LocaleEnum
    is_default: bool
    messages: Optional[Dict[str, str]]


class LanguageMessagesUpdateIn(BaseSchema):
    messages: Optional[Dict[str, str]]
