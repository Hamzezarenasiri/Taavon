from typing import Dict, Optional

from src.core import mixins
from src.main.config import collections_names


class LanguageModel(
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
):
    name: str
    icon: Optional[str]
    direction: Optional[str]
    is_default: bool = False
    messages: Optional[Dict[str, str]]

    class Config:
        collection = collections_names.LANGUAGE

    class Meta:
        collection_name = collections_names.LANGUAGE
        entity_name = "language"
