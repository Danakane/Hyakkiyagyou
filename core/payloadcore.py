from abc import ABCMeta, abstractmethod


class Payload:

    __metaclass__ = ABCMeta

    AUTHOR: str = "Danakane"

    def __init__(self) -> None:
        self.__payloadbin__: bytes = b""
        self.__size__: int = 0
        self.__optioninfo__: str = ""
        self.__shellref__: str = ""

    def set(self, payloadbin: bytes, optioninfo: str = "",
            shellref: str = "") -> None:
        self.__payloadbin__ = payloadbin
        if optioninfo:
            self.__optioninfo__ = optioninfo
        if shellref:
            self.__shellref__ = shellref
        self.__size__ = len(self.__payloadbin__)

    def size(self) -> int:
        return self.__size__

    def binary(self) -> bytes:
        return self.__payloadbin__

    @property
    def optioninfo(self) -> str:
        return self.__optioninfo__

    @property
    def shellref(self) -> str:
        return self.__shellref__

    def setup(self, host: str = "", port: int = 0) -> None:
        self.__payloadbin__ = self.parseparameters(host, port)
        self.__size__ = len(self.__payloadbin__)

    def customize(self, payloadbin: bytes, shellref: str, optioninfo: str = "") -> None:
        self.__size__ = 0
        self.__payloadbin__ = payloadbin
        self.__shellref__ = shellref
        if optioninfo:
            self.__optioninfo__ = optioninfo
        self.__size__ = len(self.__payloadbin__)

    @abstractmethod
    def parseparameters(self, host: str, port) -> bytes:
        pass
