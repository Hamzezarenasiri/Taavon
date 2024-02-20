import abc
from typing import TypeVar


class BaseDB(metaclass=abc.ABCMeta):
    """The parent class for all the databases that are to come later on.

    Inherit this class for every new concrete class that you wish to implement
    inside the `databases` directory.
    """

    @abc.abstractmethod
    async def raw_read_one(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    async def raw_read_many(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    async def raw_update(self, *args, **kwargs) -> bool:
        ...

    @abc.abstractmethod
    async def raw_delete(self, *args, **kwargs) -> bool:
        ...


DBType = TypeVar("DBType", bound=BaseDB)
