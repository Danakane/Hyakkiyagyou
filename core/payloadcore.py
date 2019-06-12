import typing

from abc import ABCMeta, abstractmethod

from shells import shellindex


class Payload:

    BIND = "bind"
    REVERSE = "reverse"

    __metaclass__ = ABCMeta

    def __init__(self)->None:
        self.__ref__: str = ""
        self.__author__: str = ""
        self.__payloadbin__: bytes = b""
        self.__size__: int = 0
        self.__optioninfo__: str = ""
        self.__shellname__: str = ""

    def set(self, payloadbin: bytes, optioninfo: str="",
            shellname: str="")->None:
        self.__payloadbin__ = payloadbin
        if optioninfo:
            self.__optioninfo__ = optioninfo
        if shellname:
            self.__shellname__: typing.Optional[typing.Callable] = shellname
        if not self.__shellname__:
            if Payload.REVERSE == self.__ref__.split("/")[0]:
                self.__shellname__ = shellindex.ShellIndex.BASICREVERSE
            else:
                self.__shellname__ = shellindex.ShellIndex.BASICBIND
        self.__size__ = len(self.__payloadbin__)

    def size(self)->int:
        return self.__size__

    def binary(self)->bytes:
        return self.__payloadbin__

    @property
    def ref(self)->str:
        return self.__ref__

    @property
    def author(self)->str:
        return self.__author__

    @property
    def optioninfo(self)->str:
        return self.__optioninfo__

    @property
    def shellname(self)->str:
        return self.__shellname__

    def setup(self, host=None, port=None)->None:
        payloadbin = self.parseparameters(host, port)
        self.set(payloadbin)

    def customize(self, author:str, ref: str, payloadbin: bytes, optioninfo: str="", shellname: str=""):
        self.__ref__ = ref
        self.__author__ = author
        self.__payloadbin__ = b""
        self.__size__ = 0
        self.__optioninfo__ = ""
        self.__shellname__ = ""
        self.set(payloadbin=payloadbin, optioninfo=optioninfo, shellname=shellname)

    @abstractmethod
    def parseparameters(self, host, port)->bytes:
        pass
