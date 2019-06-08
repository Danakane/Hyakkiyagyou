import socket

from abc import ABCMeta, abstractmethod

from pytoolcore import utils


class Scripter:

    __metaclass__ = ABCMeta

    PDUMAXSIZE: int = 65535
    TIMEOUT: float = 1

    def __init__(self, ref: str, author: str) -> None:
        self.__ref__: str = ref
        self.__author__: str = author
        self.__skt__: socket.socket = None

    def __send__(self, cmdline: str)->None:
        self.__skt__.send(utils.str2bytes(cmdline) + b"\n")

    def __recv__(self, size: int) -> str:
        return utils.bytes2str(self.__skt__.recv(size))

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

    def send(self, cmdline: str, timeout: float=TIMEOUT) -> str:
        self.__send__(cmdline)
        return self.recv(timeout)

    def postexploit(self, skt: socket.socket) -> None:
        self.__skt__ = skt
        self.execute()
        pass

    @abstractmethod
    def execute(self)-> None:
        pass
