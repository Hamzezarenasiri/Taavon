import devtools
from kavenegar import (
    APIException,
    HTTPException,
    KavenegarAPI,
)

from src.services import BaseSMS

maketrans = lambda A, B: dict((ord(a), b) for a, b in zip(A, B))  # noqa 731


class KavenegarSMS(BaseSMS):
    def __init__(self, api_key):
        self.api_key = api_key

    def sms_character_replace(self, text):
        """
            replace space in text to send by kavenegar
        :param text: text
        :type text: str
        :return: replaced space text
        :rtype: str
        """
        return (
            str(text).replace(" ", "‌").replace("_", "-").replace("_", "‌")
        )  # kavenegar error 431

    def send_sms(self, phone_number, message):
        ...

    async def send_sms_template(
        self, phone_number, template, token, token2=None, token3=None
    ):
        """
        :param phone_number: phone number
        :type phone_number: str - phone number
        :param template: sms template (kavenegar)
        :type template: str
        :param token: %token
        :type token: str
        :param token2: %token2
        :type token2: str
        :param token3: %token3
        :type token3: str
        :return: kavenegar response
        :rtype: json
        """
        devtools.debug(locals())
        try:
            api = KavenegarAPI(self.api_key)
            params = {"receptor": str(phone_number), "template": template}
            if token:
                params["token"] = self.sms_character_replace(token)
            if token2:
                params["token2"] = self.sms_character_replace(token2)
            if token3:
                params["token3"] = self.sms_character_replace(token3)
            response = api.verify_lookup(params)
            devtools.debug(response)
            return response
        except APIException as api_exception:
            devtools.debug(api_exception)
            return api_exception
        except HTTPException as http_exception:
            devtools.debug(http_exception)
            return http_exception
