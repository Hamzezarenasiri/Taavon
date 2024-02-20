import abc
from typing import TypeVar


class BaseSMS(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def send_sms(self, phone_number, message):
        ...

    @abc.abstractmethod
    async def send_sms_template(
        self, receptor, template, token, token2=None, token3=None
    ):
        ...


SMSType = TypeVar("SMSType", bound=BaseSMS)
