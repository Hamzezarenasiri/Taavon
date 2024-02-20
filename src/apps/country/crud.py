from src.core.base.crud import BaseCRUD
from .models import (
    State,
    City,
)


class StateCRUD(BaseCRUD):
    pass


state_crud = StateCRUD(
    create_db_model=State,
    read_db_model=State,
    update_db_model=State,
)


class CityCRUD(BaseCRUD):
    pass


city_crud = CityCRUD(
    create_db_model=City,
    read_db_model=City,
    update_db_model=City,
)
