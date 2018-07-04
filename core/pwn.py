import typing
import struct
import socket
import time

from os import errno
from pytoolcore import netutils
from pytoolcore import exception


class Architecture:
    x86_64: int = 0
    x86: int = 1


class Gadget:

    def __init__(self, gadgetname: str, gadgetaddr: int, base: int=0x0,
                 architecture: int = Architecture.x86_64, gadgetcomments: str = "") -> None:
        self.__gadgetname__: str = gadgetname
        self.__gadgetaddr__: int = gadgetaddr
        self.__base__: int = base
        self.__gadgetcomments__: str = gadgetcomments
        self.__architecture__: int = architecture

    def pack(self, parameters: typing.List[int]) -> None:
        representation: str = "<Q"
        if self.__architecture__ == Architecture.x86:
            representation = "<I"
        code: bytes = struct.pack(representation, self.__base__ + self.__gadgetaddr__)
        for parameter in parameters:
            code += struct.pack(representation, parameter)
        return code


class ROP:

    def __init__(self) -> None:
        self.__ropchain__: bytes = b""
        self.__gadgets__: typing.Dict[str, Gadget] = {}

    @property
    def list(self) -> typing.List[str]:
        return list(self.__gadgets__.keys())

    @property
    def chain(self):
        return self.__ropchain__

    def add(self, gadgetname: str, gadgetaddr: int, base: int,
            architecture: int = Architecture.x86_64, gadgetcomments: str = "") -> None:
        try:
            self.remove(gadgetname)
        except KeyError:
            pass
        self.__gadgets__[gadgetname] = Gadget(gadgetname, gadgetaddr, base, architecture, gadgetcomments)

    def remove(self, gadgetname) -> None:
        del self.__gadgets__[gadgetname]

    def __getitem__(self, gadgetname: str) -> Gadget:
        return self.__gadgets__[gadgetname]

    def packgadget(self, gadgetname: str, parameters: typing.List[int]) -> None:
        self.__ropchain__ += self.__gadgets__[gadgetname].pack(parameters)

    def pack(self, addr, architecture: int=Architecture.x86_64):
        representation: str = "<Q"
        if architecture == Architecture.x86_64:
            representation = "<I"
        self.__ropchain__ += struct.pack(representation, addr)

    def clear(self)->None:
        self.__ropchain__ = b""


class RemoteProcess:

    def __init__(self, rsockaddr: typing.Tuple[typing.Any, ...]) -> None:
        self.__rsockaddr__: typing.Tuple[typing.Any, ...] = rsockaddr
        self.__skt__: socket.socket = None

    def connect(self) -> None:
        self.disconnect()
        protocol3: int = netutils.host2protocol(self.__rsockaddr__[0])
        self.__skt__: socket.socket = socket.socket(protocol3, socket.SOCK_STREAM)
        try:
            self.__skt__.connect(self.__rsockaddr__)
        except(socket.error, socket.herror, socket.gaierror, socket.timeout) as err:
            self.disconnect()
            raise (exception.CException(str(err)))

    def disconnect(self) -> None:
        if self.__skt__ is not None:
            self.__skt__.close()
            self.__skt__ = None

    def clear(self, timeout: float = 0.02, sleepelapse: float = 0.01):
        time.sleep(sleepelapse)
        self.__skt__.settimeout(timeout)
        try:
            while self.__skt__.recv(4096):
                pass
        except socket.timeout:
            pass
        self.__skt__.settimeout(None)

    def alive(self, sleepelapse: float = 0.01) -> bool:
        alive: bool = True
        self.__skt__.setblocking(False)
        for i in range(50):
            try:
                self.__skt__.recv(1)
                alive = False
                break
            except socket.error as err:
                errcode = err.args[0]
                if errcode == errno.EAGAIN:
                    time.sleep(sleepelapse)
                else:
                    alive = False
                    break
        return alive

    def recv(self, size: int, timeout: int=0) -> bytes:
        if timeout:
            self.__skt__.settimeout(timeout)
        res: bytes = self.__skt__.recv(size)
        self.__skt__.settimeout(None)
        return res

    def send(self, stuff) -> None:
        self.__skt__.send(stuff)
