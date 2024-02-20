from typing import TypeVar, Optional, Type

from src.main.config import AdminSettings
from src.services.cache.base import BaseCache, CacheType
from src.services.db.base import BaseDB, DBType
from src.services.email import BaseEmail, EmailType
from src.services.sms import BaseSMS, SMSType

T = TypeVar("T")


class Services(object):
    ADMIN_SETTINGS: Optional[AdminSettings] = None
    BROKER: T = None
    CACHE: Optional[CacheType] = None
    DB: Optional[DBType] = None
    SYNC_DB: Optional[DBType] = None
    EMAIL: Optional[EmailType] = None
    GOOGLE: T = None
    LOGGER: T = None
    SMS: Optional[SMSType] = None


global_services = Services()
