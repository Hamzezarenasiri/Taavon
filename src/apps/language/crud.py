from src.apps.language.models import (
    LanguageModel,
)
from src.core.base.crud import BaseCRUD


class LanguageCRUD(BaseCRUD):
    pass


languages_crud = LanguageCRUD(
    read_db_model=LanguageModel,
    create_db_model=LanguageModel,
    update_db_model=LanguageModel,
)
