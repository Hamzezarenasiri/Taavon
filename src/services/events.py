import logging

from pymongo import MongoClient
from pymongo.database import Database

from src.core.logger import create_logger
from src.main import config
from src.services import SMSType, EmailType
from src.services.cache.base import CacheType
from src.services.cache.redis import Redis
from src.services.db.base import DBType
from src.services.db.mongodb import MongoDB
from src.services.email.SimpleHtmlEmail import SimpleHtmlGmail
from src.services.sms.kavenegar import KavenegarSMS


async def initialize_logger() -> logging.Logger:
    return create_logger(__name__, config.app_settings.LOG_LEVEL)


async def initialize_cache() -> CacheType:
    redis = Redis()
    await redis.connect(
        host=config.cache_settings.HOST,
        port=config.cache_settings.PORT,
        db=config.cache_settings.DB,
        password=config.cache_settings.PASSWORD,
        timeout=config.cache_settings.TIMEOUT_SECONDS,
    )
    return redis


async def initialize_db() -> DBType:
    mongo = MongoDB()

    await mongo.connect(
        uri=config.db_settings.URI,
        connection_timeout=config.db_settings.CONNECTION_TIMEOUT,
        min_pool_size=config.db_settings.MIN_POOL_SIZE,
        max_pool_size=config.db_settings.MAX_POOL_SIZE,
    )

    await mongo.get_database(database_name=config.db_settings.DATABASE_NAME)
    return mongo


def sync_db() -> Database:
    client = MongoClient(
        config.db_settings.URI,
    )

    return client[config.db_settings.DATABASE_NAME]


async def initialize_sms() -> SMSType:
    return KavenegarSMS(config.sms_settings.api_key)


async def initialize_email() -> EmailType:
    return SimpleHtmlGmail(
        default_from_email=config.email_settings.DEFAULT_FROM_EMAIL,
        password=config.email_settings.PASSWORD,
    )


async def close_db_connection(db: MongoDB) -> None:
    await db.disconnect()
