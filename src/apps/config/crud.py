from src.apps.config.models import (
    Config,
)
from src.core.base.crud import BaseCRUD
from src.main.config import AdminSettings, admin_settings


class ConfigCRUD(BaseCRUD):
    async def get_configs_object(self):
        config = await self.get_object(raise_exception=False)
        if not config:
            # await self.create(self.create_db_model(**admin_settings.dict()))
            return admin_settings
        return AdminSettings(
            **config.dict(
                exclude={
                    "id",
                    "update_datetime",
                    "create_datetime",
                    "is_enabled",
                    "is_deleted",
                }
            )
        )


configs_crud = ConfigCRUD(
    read_db_model=Config,
    create_db_model=Config,
    update_db_model=Config,
)
