import asyncio
import os
from contextlib import asynccontextmanager
from typing import Callable, Any

from beanie import init_beanie

from src import services
from src.core.base.db_utils import (
    create_fixtures,
    get_models,
)
from src.main.config import app_settings, db_settings
from src.services import global_services, events


@asynccontextmanager
async def lifespan(_: Any):
    services.global_services.LOGGER = await events.initialize_logger()
    services.global_services.LOGGER.info("LOGGER Connected :)")
    services.global_services.DB = await events.initialize_db()
    services.global_services.SYNC_DB = events.sync_db()
    services.global_services.LOGGER.info("DB Connected :)")
    await init_beanie(
        database=getattr(services.global_services.DB.client, db_settings.DATABASE_NAME),
        document_models=(
            get_models(app_settings, logger=services.global_services.LOGGER)
        ),
    )
    services.global_services.LOGGER.info("DB Initialized :)")
    services.global_services.CACHE = await events.initialize_cache()
    services.global_services.LOGGER.info("CACHE Connected :)")
    # services.global_services.ADMIN_SETTINGS = await configs_crud.get_configs_object()
    # services.global_services.LOGGER.info("Set Admin Configs")
    services.global_services.SMS = await events.initialize_sms()
    services.global_services.LOGGER.info("Sms Connected :)")
    services.global_services.EMAIL = await events.initialize_email()
    services.global_services.LOGGER.info("Email Connected :)")
    await asyncio.gather(
        # create_indexes(
        #     db_engine=services.global_services.DB._engine,
        #     app_settings=app_settings,
        #     logger=services.global_services.LOGGER,
        # ),
        create_fixtures(
            app_settings=app_settings, logger=services.global_services.LOGGER
        ),
    )
    if not os.path.exists(app_settings.DEFAULT_FILES_PATH):
        os.makedirs(app_settings.DEFAULT_FILES_PATH)
        services.global_services.LOGGER.info("File Path Created :)")
    services.global_services.LOGGER.info("running ... :)")
    yield
    print("shutting down...")
    await events.close_db_connection(global_services.DB)
    services.global_services.LOGGER.info("entries deleted")


def create_start_app_handler() -> Callable:
    async def start_app() -> None:
        pass

    # async def set_admin_settings():
    #     services.global_services.ADMIN_SETTINGS = (
    #         await configs_crud.get_configs_object()
    #     )
    #     services.global_services.LOGGER.info("Set Admin Configs")
    #
    # async def set_cache_connection():
    #     services.global_services.CACHE = await events.initialize_cache()
    #     services.global_services.LOGGER.info("CACHE Connected :)")

    # async def set_db_connection():
    #     services.global_services.DB = await events.initialize_db()
    #     services.global_services.LOGGER.info("DB Connected :)")

    # async def set_logger():
    #     services.global_services.LOGGER = await events.initialize_logger()
    #     services.global_services.LOGGER.info("LOGGER Connected :)")

    # async def set_sms():
    #     services.global_services.SMS = await events.initialize_sms()
    #     services.global_services.LOGGER.info("Sms Connected :)")
    #
    # async def set_email():
    #     services.global_services.EMAIL = await events.initialize_email()
    #     services.global_services.LOGGER.info("Email Connected :)")

    # @repeat_every_day_on(on_time=time(15, 0))
    # async def email_waiting_baskets_task() -> None:
    #     services.global_services.LOGGER.info("Run waiting baskets task")

    return start_app


def create_stop_app_handler() -> Callable:
    async def stop_app() -> None:
        print("shutting down...")
        await events.close_db_connection(global_services.DB)
        services.global_services.LOGGER.info("entries deleted")

    return stop_app
