import typing
import struct
import socket
import time
import errno
from abc import ABCMeta
from pytoolcore import netutils
from pytoolcore import exception


class Architecture:
    x86_64: int = 0
    x86: int = 1


class ROPChainElement:
    __metaclass__ = ABCMeta

    def __init__(self, raw: bytes):
        self.__raw__ = raw

    @property
    def raw(self) -> bytes:
        return self.__raw__


class Gadget:

    def __init__(self, gadgetname: str, gadgetaddr: int, base: int=0x0, nbparameters: int = 0,
                 architecture: Architecture = Architecture.x86_64, gadgetcomments: str = "") -> None:
        self.__gadgetname__: str = gadgetname
        self.__gadgetaddr__: int = gadgetaddr
        self.__base__: int = base
        self.__gadgetcomments__: str = gadgetcomments
        self.__architecture__: Architecture = architecture
        self.__nbparameters__: int = nbparameters


class GadgetInstance(ROPChainElement):

    def __init__(self, gadget: Gadget, parameters: typing.List[int]) -> None:
        self.__gadgetname__ = gadget.__gadgetname__
        self.__gadgetaddr__: int = gadget.__gadgetaddr__
        self.__base__: int = gadget.__base__
        self.__architecture__: Architecture = gadget.__architecture__
        self.__lines__: typing.List[str] = []
        raw: bytes = b""
        representation: str = "<Q"
        if self.__architecture__ == Architecture.x86:
            representation = "<I"
        if gadget.__nbparameters__ > 0:
            for parameter in parameters:
                rawline: bytes = struct.pack(representation, parameter)
                raw += rawline
                self.__lines__.append("0x" + rawline.hex())
        super(ROPChainElement, self).__init__(raw=raw)

    def dump(self, start: int = 0) -> typing.Tuple(str, int):
        representation: str = "<Q"
        rawaddress: int = start
        linesize: int = 8
        stackfragment: str = ""
        if self.__architecture__ == Architecture.x86:
            representation = "<I"
            linesize = 4
        for line in self.__lines__:
            rawaddress += linesize
            stackfragment += "0x" + struct.pack(representation, rawaddress).hex() + ":\t\t" + line + "\n"
        return typing.Tuple(stackfragment, start + len(self.__lines__) * linesize)


class StackElement(ROPChainElement):

    def __init__(self, value: int,  architecture: Architecture):
        self.__value__: int = value
        self.__architecture__: Architecture = architecture
        representation: str = "<Q"
        if self.__architecture__ == Architecture.x86:
            representation = "<I"
        super(ROPChainElement, self).__init__(raw=struct.pack(representation, self.__value__))


class ROP:

    def __init__(self, base: int = 0, architecture: int = Architecture.x86_64) -> None:
        self.__ropchain__: typing.List[ROPChainElement] = []
        self.__gadgets__: typing.Dict[str, Gadget] = {}
        self.__architecture__: Architecture = architecture
        self.__base__: int = base

    @property
    def base(self):
        return self.__base__

    @property
    def chain(self):
        return self.__ropchain__

    def add(self, gadgetname: str, gadgetaddr: int, nbparameters: int, gadgetcomments: str = "") -> None:
        try:
            self.remove(gadgetname)
        except KeyError:
            pass
        self.__gadgets__[gadgetname] = Gadget(gadgetname, gadgetaddr, self.__base__, nbparameters,
                                              self.__architecture__, gadgetcomments)

    def remove(self, gadgetname) -> None:
        del self.__gadgets__[gadgetname]

    def __getitem__(self, gadgetname: str) -> Gadget:
        return self.__gadgets__[gadgetname]

    def packgadget(self, gadgetname: str, *parameters: int) -> None:
        self.__ropchain__ += GadgetInstance(self.__gadgets__[gadgetname], list(parameters))

    def pack(self, addr: int):
        self.__ropchain__ += StackElement(addr, self.__architecture__)

    def clear(self, base: int = 0)->None:
        self.__ropchain__ = []
        self.__base__ = base

    def dump(self, stackaddress: int = 0) -> str:
        pass


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
            raise (exception.ErrorException(str(err)))

    def disconnect(self) -> None:
        if self.__skt__ is not None:
            self.__skt__.close()
            self.__skt__ = None

    def clear(self, timeout: float = 0.01, sleepelapse: float = 0.01):
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
        for i in range(100):
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
