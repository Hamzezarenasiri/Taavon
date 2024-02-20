from src.core.base.crud import BaseCRUD
from .models import (
    Report,
)


class ReportCRUD(BaseCRUD):
    pass


report_crud = ReportCRUD(
    read_db_model=Report,
    create_db_model=Report,
    update_db_model=Report,
)
