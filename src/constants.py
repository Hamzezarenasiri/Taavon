from enum import Enum
from typing import List
from src.fastapi_babel import _


class CountryCode(str, Enum):
    iran: str = "IR"


ALL_COUNTRY_CODES = [i.value for i in CountryCode.__members__.values()]


class ErrorMessageEnum(str, Enum):
    access_denied: str = _("Can not perform this action")


class ErrorDetailEnum(List[str], Enum):
    access_denied: List[str] = [ErrorMessageEnum.access_denied]
