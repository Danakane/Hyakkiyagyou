import socket
import threading
import typing

from abc import ABCMeta, abstractmethod

from pytoolcore import style
from pytoolcore import netutils
from pytoolcore import utils
from core import exploitcore


class RemoteShell:
    __metaclass__ = ABCMeta

    def __init__(self, exploit: exploitcore.Exploit, rhost: str, rport: int,
                 lhost: str="", lport: int=0)->None:
        self.__exploit__: exploitcore.Exploit = exploit
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
    def configure(self) -> None:
        pass


class AsynchronousBasicRemoteShell(RemoteShell):
    __metaclass__ = ABCMeta

    PDUMAXSIZE = 65535

    def __init__(self, exploit: exploitcore.Exploit, rhost: str, rport: int,
                 lhost: str="", lport: int=0)->None:
        RemoteShell.__init__(self, exploit, rhost, rport, lhost, lport)
        self.__recvthrd__: threading.Thread = threading.Thread()

    def __send__(self, cmdline: str)->None:
        self.__shellskt__.send(utils.str2bytes(cmdline) + b"\n")

    def __recv__(self, size: int)->str:
        return utils.bytes2str(self.__shellskt__.recv(size))

    def __recvloop__(self)->None:
        while self.__running__:
            try:
                print(self.__recv__(AsynchronousBasicRemoteShell.PDUMAXSIZE), end="")
            except(UnicodeDecodeError, UnicodeEncodeError):
                pass

    def run(self)->None:
        self.configure()
        self.__shellskt__.setblocking(False)

        self.__recvthrd__ = threading.Thread(target=self.__recvloop__)
        self.__running__ = True
        self.__recvthrd__.start()
        try:
            while True:
                cmdline: str = input()
                self.__send__(cmdline)
                if cmdline == "exit":
                    break
        except (KeyboardInterrupt, SystemExit):
            self.__send__("exit")
            print()
        except(socket.error, socket.herror, socket.gaierror, socket.timeout) as err:
            self.__send__("exit")
            print(style.Style.error(str(err)))
        finally:
            self.__running__ = False
            self.__recvthrd__.join()
            self.__shellskt__.close()

    @abstractmethod
    def configure(self) -> None:
        pass


class SynchronousBashRemoteShell(RemoteShell):
    # Synchronous remote bash shell
    __metaclass__ = ABCMeta

    PDUMAXSIZE = 65535
    SLEEPTIME = 0.5

    def __init__(self, exploit: exploitcore.Exploit, rhost, rport, lhost="", lport=0)->None:
        RemoteShell.__init__(self, exploit, rhost, rport, lhost, lport)

    def __send__(self, cmdline: str)->None:
        self.__shellskt__.send(utils.str2bytes(cmdline) + b"\n")

    def __recv__(self, size: int):
        return utils.bytes2str(self.__shellskt__.recv(size))

    def run(self):
        self.configure()
        prompt: str = self.__recv__(SynchronousBashRemoteShell.PDUMAXSIZE)
        # Some black magic here ;)
        # In fact prompt = some bytes + @ + hostname + : + something that doesn't matter
        hostname: str = prompt.split("@")[1].split(":")[0]
        try:
            while True:
                cmdline: str = input(prompt)
                self.__send__(cmdline)
                if cmdline == "exit":
                    break
                res: str = self.__recv__(SynchronousBashRemoteShell.PDUMAXSIZE)
                # while not prompt (prompt doesn't end with '\n')
                while res[len(res) - 1] == "\n" or len(res.split("@")) == 1 or \
                        res.split("@")[1].split(":")[0] != hostname:
                    print(res, end="")
                    # prompt return
                    res = self.__recv__(SynchronousBashRemoteShell.PDUMAXSIZE)
                prompt = res
        except (KeyboardInterrupt, SystemExit):
            self.__send__("exit")
            print()
        except(socket.error, socket.herror, socket.gaierror, socket.timeout) as err:
            self.__send__("exit")
            print(style.Style.error(str(err)))
        finally:
            self.__shellskt__.close()

    @abstractmethod
    def configure(self) -> None:
        pass
