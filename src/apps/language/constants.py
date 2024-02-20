from enum import Enum
from typing import Dict


class LocaleEnum(str, Enum):
    arabic_uae: str = "ar"
    english: str = "en"


class LanguageEnum(str, Enum):
    arabic: str = "AR-AE"
    english: str = "EN"


ALL_LANGUAGES = [i.value for i in LanguageEnum.__members__.values()]
ALL_LANGUAGES_KEYS = LanguageEnum.__members__.keys()
MultiLanguageField = Dict[LanguageEnum, str]
