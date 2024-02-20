import pickle
from enum import Enum
from string import digits
from typing import Optional

from fastapi import HTTPException

from src.apps.auth.constants import AuthOTPTypeEnum
from src.apps.user.models import User
from src.core.common.exceptions import CustomHTTPException
from src.core.utils import get_random_string
from src.main.config import app_settings, test_settings
from src.services import global_services


class OtpRequestType(str, Enum):
    reset_pass: str = "rest_password"
    verification: str = "verification"


class OtpExistsError(Exception):
    pass


async def otp_sender(
    user: User,
    otp_type: AuthOTPTypeEnum,
    otp: str,
    request_type: Optional[OtpRequestType] = OtpRequestType.reset_pass,
) -> str:
    message = app_settings.OTP_TEMPLATE.format(otp=otp)
    if otp_type == AuthOTPTypeEnum.sms:
        await global_services.SMS.send_sms_template(
            phone_number=user.mobile_number,
            template=app_settings.SMS_OTP_TEMPLATE,
            token=otp,
        )
        # global_services.BROKER.send_task(
        #     name="twilio_send_sms_task_high",
        #     queue="high_priority",
        #     kwargs={"mobile_number": user.mobile_number, "message": message},
        # )
    elif otp_type == AuthOTPTypeEnum.email:
        # global_services.BROKER.send_task(
        #     name="twilio_send_email_task_high",
        #     queue="high_priority",
        #     kwargs={"to_email": user.email, "subject": message, "content": message},
        # )
        if request_type == OtpRequestType.reset_pass:
            global_services.EMAIL.send_otp_rest_pass_email(
                user.email,
                otp_code=otp,
                user_name=f"{user.first_name} {user.last_name}",
            )
        if request_type == OtpRequestType.verification:
            global_services.EMAIL.send_otp_verification_email(
                user.email,
                otp_code=otp,
                user_name=f"{user.first_name} {user.last_name}",
            )
    else:
        raise HTTPException(status_code=406, detail="Invalid otp type")
    return message


async def set_otp(key: str, otp_type):
    exist_key = await global_services.CACHE.exists(key=key)
    if exist_key:
        message = f"{otp_type} has already been sent, try again after the time limit "
        raise CustomHTTPException(
            detail=[message],
            message=message,
            status_code=406,
        )
    if app_settings.TEST_MODE:
        otp = test_settings.DEFAULT_OTP
        expiry = test_settings.DEFAULT_OTP_TIME
    else:
        otp = make_random_digit_otp(length=app_settings.OTP_LENGTH)
        expiry = app_settings.OTP_TIME
    otp_to_cache = pickle.dumps(otp)
    await global_services.CACHE.set(key=key, value=otp_to_cache, expiry=expiry)
    return otp


async def set_otp_and_send_message(
    user: User,
    otp_type: AuthOTPTypeEnum,
    cache_key: Optional[str] = None,
    request_type: Optional[OtpRequestType] = OtpRequestType.reset_pass,
) -> str:
    cache_key = cache_key or str(user.id)
    otp = await set_otp(cache_key, otp_type)
    return await otp_sender(user, otp_type, otp, request_type=request_type)


async def get_otp(key: str) -> Optional[str]:
    cached = await global_services.CACHE.get(key=key)
    if cached:
        return pickle.loads(cached)


def make_random_digit_otp(length=6, allowed_chars=digits[1:]):
    return get_random_string(length, allowed_chars)
