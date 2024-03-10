from typing import Dict, List, Optional, Union

from pydantic import (
    AnyUrl,
    BaseSettings as PydanticBaseSettings,
    validator,
    EmailStr,
    HttpUrl,
)

from src.apps.config.common_model import OfficeAddress
from src.apps.language.constants import LanguageEnum

__all__ = (
    "admin_settings",
    "api_settings",
    "app_settings",
    "cache_settings",
    "collections_names",
    "db_settings",
    "jwt_settings",
    "region_settings",
    "test_settings",
)

from src.constants import CountryCode


class BaseSettings(PydanticBaseSettings):
    class Config(PydanticBaseSettings.Config):
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class AppSettings(BaseSettings):
    FRONT_URL: Optional[HttpUrl] = "https://virapayesh.ir"
    OTP_LENGTH: int = 5
    OTP_TIME: int = 2 * 60
    PROJECT_NAME: str = "Vira TAAVON Website"
    PROJECT_DESCRIPTION: str = "Vira TAAVON Website"
    LOG_LEVEL: str = "INFO"
    PROJECT_SERVERS: List[Dict[str, str]] = [
        {"url": "https://taavon-api.virapayesh.ir"},
        {"url": "http://localhost:8000"},
    ]
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DEBUG: bool = False
    SENDER_EMAIL: str = "support@virarayan.com"
    REPLY_RECEIVER_EMAIL: str = "support@virarayan.com"
    OTP_TEMPLATE: str = "Vira TAAVON verification code: {otp}"
    SMS_OTP_TEMPLATE: str = "vira-reset-pass"
    OTP_SUBJECT: str = "Vira TAAVON One-Time Password"
    SMS_PRODUCT_NOTIFICATION_TEMPLATE: str = "Vira-taavon-notif"
    USER_AVATAR_MAX_FILE_SIZE: int = 100 * 2**20  # 100MB
    DEFAULT_MAX_STR_LENGTH: int = 3145728  # 3MB
    USER_AVATAR_SUPPORTED_FORMATS: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/svg+xml",
    ]
    APP_RELOAD: Optional[bool] = False
    REQUEST_ATTACHMENT_MAX_FILE_SIZE: int = 2**30 * 2
    REQUEST_ATTACHMENT_SUPPORTED_FORMATS: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/svg+xml",
        "video/x-flv",
        "video/mp4",
        "application/x-mpegURL",
        "video/MP2T",
        "video/3gpp",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-ms-wmv",
    ]
    SUBJECT_EMAIL_PRODUCT_NOTIFICATION: str = "آسیب پذیری گزارش شده"
    CRYPTO_KEY: str = "Behtarin_S3cr3t_k3y"
    TEST_MODE: bool = False
    SENTRY_DSN: Optional[str] = None
    DEFAULT_LANGUAGE: LanguageEnum = LanguageEnum.english
    DEFAULT_COUNTRY_CODE: CountryCode = CountryCode.iran
    DEFAULT_MEDIA_PATH: str = "media"
    DEFAULT_FILES_PATH: str = f"{DEFAULT_MEDIA_PATH}/files"
    DEFAULT_AVATARS_PATH: str = f"{DEFAULT_MEDIA_PATH}/users/avatars"
    DEFAULT_PASSWORD: str = "hNzrH4'7<-"
    APPS_FOLDER_NAME: str = "src/apps"
    APPS: List[str] = [
        "product",
        "auth",
        "category",
        "config",
        "country",
        "file",
        "language",
        "log_app",
        "notification",
        "organization",
        "report",
        "user",
        "store",
        "invoice",
    ]


app_settings = AppSettings()


class FilePaths(BaseSettings):
    DEFAULT_MEDIA_PATH: str = "src/media"

    class Config(BaseSettings.Config):
        env_prefix = "FILES_"


file_paths = FilePaths()


class CollectionsNames(BaseSettings):
    PRODUCT: str = "Product"
    CITY: str = "City"
    ORGANIZATION: str = "Organization"
    CATEGORY: str = "Category"
    CONFIG: str = "Config"
    ENTITY: str = "Entity"
    FILE: str = "File"
    INVOICE: str = "Invoice"
    ROLE: str = "Role"
    LANGUAGE: str = "Language"
    LOG: str = "Log"
    NOTIFICATION: str = "Notification"
    RULE: str = "Rule"
    REPORT: str = "Report"
    STATE: str = "State"
    USER: str = "User"
    PROFILE: str = "Profile"
    DASHBOARD: str = "Dashboard"
    STORE: str = "Store"


collections_names = CollectionsNames()


class RegionSettings(BaseSettings):
    DEFAULT: str = "IR"

    class Config(BaseSettings.Config):
        env_prefix = "REGION_"


region_settings = RegionSettings()


class DBSettings(BaseSettings):
    URI: str
    DATABASE_NAME: str = "Taavon"
    MIN_POOL_SIZE: int = 10
    MAX_POOL_SIZE: int = 50
    CONNECTION_TIMEOUT: int = 10000

    class Config(BaseSettings.Config):
        env_prefix = "DB_"


db_settings = DBSettings()


class SmsSettings(BaseSettings):
    api_key: str = "6B45336C447134306667597254695A73786349467848494C5266754435735051"

    class Config(BaseSettings.Config):
        env_prefix = "SMS_"


sms_settings = SmsSettings()


class EmailSettings(BaseSettings):
    DEFAULT_FROM_EMAIL: str = "vira.taavon.rayan@gmail.com"
    PASSWORD: str = "....................."

    class Config(BaseSettings.Config):
        env_prefix = "EMAIL_"


email_settings = EmailSettings()


class ApiSettings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    BACKEND_CORS_METHODS: List[str] = ["*"]
    BACKEND_CORS_HEADERS: List[str] = ["*"]

    # pylint: disable=no-self-argument,no-self-use
    @validator("BACKEND_CORS_ORIGINS", pre=True, allow_reuse=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config(BaseSettings.Config):
        env_prefix = "API_"


api_settings = ApiSettings()


class CacheSettings(BaseSettings):
    HOST: str
    PORT: int = 6379
    DB: int = 2
    PASSWORD: Optional[str]
    TIMEOUT_SECONDS: Optional[int] = 5

    class Config(BaseSettings.Config):
        env_prefix = "CACHE_"


cache_settings = CacheSettings()


class JWTSettings(BaseSettings):
    SECRET_KEY: str = "qvHMJ/hx7HsfGNTfA2cRZf29nGK+jpiUS87GH6AhtB1fsXG8SYCFSWJ18nPcKTdm"
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 1800
    REFRESH_TOKEN_LIFETIME_SECONDS: int = 43200
    ALGORITHM: str = "HS256"

    class Config(BaseSettings.Config):
        env_prefix = "JWT_"


jwt_settings = JWTSettings()


class TestSettings(BaseSettings):
    DEFAULT_PASS: str = "pass_test"
    DEFAULT_PASS2: str = "1234 qwer"
    DEFAULT_OTP: str = "12345"
    DEFAULT_OTP_TIME: int = 5
    DEFAULT_EMAIL: str = "hamzezn@gmail.com"
    DEFAULT_PHONE: str = "+989127634520"

    class Config(BaseSettings.Config):
        env_prefix = "TEST_"


test_settings = TestSettings()


class GoogleSettings(BaseSettings):
    CLIENT_ID: str = (
        "395365840836-rv6eqh098te9h8c4pg9o5fjg8i7oev5n.apps.googleusercontent.com"
    )
    CLIENT_SECRET: str = "hLhWlRLwVSZryj-K_mXuy8-t"
    LOGIN_REDIRECT_URI: AnyUrl = str(
        app_settings.PROJECT_SERVERS[0]["url"]
        + api_settings.API_V1_STR
        + "/auth/login/google"
    ).replace("http://", "https://")

    class Config(BaseSettings.Config):
        env_prefix = "GOOGLE_"


google_settings = GoogleSettings()


class AdminSettings(BaseSettings):
    is_deleted: Optional[bool] = True
    office_address: Optional[OfficeAddress] = OfficeAddress()
    other_configs: Optional[dict] = {}
    default_email_recipients: Optional[List[EmailStr]] = []

    class Config(BaseSettings.Config):
        env_prefix = "ADMIN_"
        arbitrary_types_allowed = True


admin_settings = AdminSettings()
