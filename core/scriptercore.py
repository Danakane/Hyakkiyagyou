import socket
import typing

from abc import ABCMeta, abstractmethod

from pytoolcore import utils


class Scripter:

    __metaclass__ = ABCMeta

    PDUMAXSIZE: int = 65535
    TIMEOUT: float = 1

    def __init__(self) -> None:
        self.__skt__: typing.Optional[socket.socket] = None
        self.__parameters__: typing.Dict[str, str] = {}
        self.__configure__: typing.Callable = lambda **kwargs: None

    @property
    def parameters(self) -> typing.Dict[str, str]:
        return self.__parameters__

    @property
    def configure(self) -> typing.Callable:
        return self.__configure__

    @configure.setter
    def configure(self, configfct: typing.Callable) -> None:
        self.__configure__ = configfct

    def __send__(self, cmdline: str) -> None:
        self.__skt__.send(utils.str2bytes(cmdline) + b"\n")

    def __recv__(self, size: int) -> str:
        return utils.bytes2str(self.__skt__.recv(size))

    def customize(self, parameters: typing.Dict[str, str]):
        self.__parameters__ = parameters

    def recv(self, timeout: float) -> str:
        self.__skt__.settimeout(timeout)
        res: str = ""
        try:
            while True:  # will always trigger the exception
                res += self.__recv__(Scripter.PDUMAXSIZE)
        except (socket.error, socket.herror, socket.gaierror, socket.timeout):
            if len(res.split("\n")) > 1:
                res = "\n".join(res.split("\n")[1:])
        finally:
            self.__skt__.settimeout(None)
        return res

    def send(self, cmdline: str, timeout: float = TIMEOUT) -> str:
        self.__send__(cmdline)
        return self.recv(timeout)

    def execute(self, skt: socket.socket) -> None:
        self.__skt__ = skt
        self.dojob()
        pass

    @abstractmethod
    def dojob(self) -> None:
        pass
