import typing

from abc import ABCMeta


class Payload:

    __metaclass__ = ABCMeta

    AUTHOR: str = "Danakane"

    def __init__(self) -> None:
        self.__raw__: bytes = b""
        self.__size__: int = 0
        self.__shellref__: str = ""
        self.__parameters__: typing.Dict[str, str] = {}
        self.__configure__: typing.Callable = lambda **kwargs: None

    @property
    def raw(self) -> bytes:
        return self.__raw__

    @raw.setter
    def raw(self, value: bytes) -> None:
        self.__raw__ = value
        self.__size__ = len(self.__raw__)

    @property
    def size(self) -> int:
        return self.__size__

    @property
    def shellref(self) -> str:
        return self.__shellref__

    @property
    def parameters(self) -> typing.Dict[str, str]:
        return self.__parameters__

    @property
    def configure(self) -> typing.Callable:
        return self.__configure__

    @configure.setter
    def configure(self, configfct: typing.Callable) -> None:
        self.__configure__ = configfct

    @property
    def bindport(self) -> int:
        return 0

    def customize(self, raw: bytes, shellref: str, parameters: typing.Dict[str, str]) -> None:
        self.raw = raw
        self.__shellref__ = shellref
        self.__parameters__ = parameters
