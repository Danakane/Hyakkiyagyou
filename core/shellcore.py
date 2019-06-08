import socket
import threading
import typing
import sys

from abc import ABCMeta, abstractmethod

from pytoolcore import style
from pytoolcore import netutils
from pytoolcore import utils
from core import exploitcore, scriptercore


class RemoteShell:
    __metaclass__ = ABCMeta

    def __init__(self, exploit: exploitcore.Exploit, scripter: scriptercore.Scripter,
                 rhost: str, rport: int, lhost: str="", lport: int=0)->None:
        self.__exploit__: exploitcore.Exploit = exploit
        self.__scripter__: scriptercore.Scripter = scripter
        self.__rhost__: str = str(rhost)
        self.__rport__: int = int(rport)
        self.__lhost__: str = str(lhost)
        self.__lport__: int = int(lport)
        self.__rsockaddr__: typing.Tuple[typing.Any, ...] = ()
        self.__lsockaddr__: typing.Tuple[typing.Any, ...] = ()
        self.__shellskt__: socket.socket = socket.socket()
        self.__running__: bool = False
        self.__protocol__: int = 0
        rsockinfo: typing.Tuple[int, int, int, str, typing.Tuple[typing.Any, ...]] \
            = netutils.getsockinfo(rhost, rport)
        self.__rsockaddr__ = rsockinfo[4]
        if lhost:
            lsockinfo = netutils.getsockinfo(lhost, lport)
            self.__lsockaddr__ = lsockinfo[4]
            self.__protocol__ = lsockinfo[0]
        else:
            self.__protocol__ = rsockinfo[0]
        if not self.__protocol__ or \
                (lhost and self.__protocol__ != netutils.host2protocol(rhost)):
            raise ValueError("Missing or invalid RHOST/LHOST parameter(s)")
        pass

    @abstractmethod
    def run(self)->None:
        pass

    @property
    def protocol(self) -> int:
        return self.__protocol__

    @property
    def rsockaddr(self) -> typing.Tuple[typing.Any, ...]:
        return self.__rsockaddr__

    @property
    def lsockaddr(self) -> typing.Tuple[typing.Any, ...]:
        return self.__lsockaddr__

    @property
    def shellskt(self)->socket.socket:
        return self.__shellskt__

    @shellskt.setter
    def shellskt(self, shellskt: socket.socket)->None:
        self.__shellskt__ = shellskt

    @property
    def exploit(self)-> exploitcore.Exploit:
        return self.__exploit__

    @property
    def scripter(self)-> scriptercore.Scripter:
        return self.__scripter__

    @property
    def rhost(self)->str:
        return self.__rhost__

    @property
    def lhost(self)->str:
        return self.__lhost__

    @property
    def rport(self)->int:
        return self.__rport__

    @property
    def lport(self)->int:
        return self.__lport__

    @abstractmethod
    def initialize(self) -> None:
        pass


class AsynchronousBasicRemoteShell(RemoteShell):
    __metaclass__ = ABCMeta

    PDUMAXSIZE = 65535

    def __init__(self, exploit: exploitcore.Exploit, scripter: scriptercore.Scripter,
                 rhost: str = "", rport: int = 0, lhost: str="", lport: int=0)->None:
        RemoteShell.__init__(self, exploit, scripter, rhost, rport, lhost, lport)
        self.__recvthrd__: threading.Thread = threading.Thread()
        self.__lastcmd__: str = ""

    def __send__(self, cmdline: str)->None:
        self.__shellskt__.send(utils.str2bytes(cmdline) + b"\n")

    def __recv__(self, size: int)->str:
        return utils.bytes2str(self.__shellskt__.recv(size))

    def __recvloop__(self)->None:
        while self.__running__:
            try:
                res: str = self.__recv__(AsynchronousBasicRemoteShell.PDUMAXSIZE)
                if res != self.__lastcmd__:
                    print(res, end="")
                    sys.stdout.flush()
            except socket.error:
                pass
            except(UnicodeDecodeError, UnicodeEncodeError):
                pass

    def run(self)->None:
        self.initialize()
        if self.scripter is not None:
            self.scripter.postexploit(self.__shellskt__)
        self.__shellskt__.setblocking(False)
        self.__recvthrd__ = threading.Thread(target=self.__recvloop__)
        self.__running__ = True
        self.__recvthrd__.start()
        try:
            self.__send__("")
            while True:
                cmdline: str = input()
                self.__lastcmd__ = cmdline + "\n"
                self.__send__(cmdline)
                if cmdline == "exit":
                    break
        except (KeyboardInterrupt, SystemExit):
            self.__send__("exit\n")
            print()
        except(socket.error, socket.herror, socket.gaierror, socket.timeout) as err:
            print(style.Style.error(str(err)))
        finally:
            self.__running__ = False
            self.__recvthrd__.join()
            self.__shellskt__.close()

    @abstractmethod
    def initialize(self) -> None:
        pass
