import socket
import threading
import typing
import sys

from abc import ABCMeta, abstractmethod

from pytoolcore import style
from pytoolcore import netutils
from pytoolcore import utils
from core import exploitcore, scriptercore


class Shell:
    __metaclass__ = ABCMeta

    AUTHOR: str = "Danakane"

    def __init__(self) -> None:
        self.__exploit__: typing.Optional[exploitcore.Exploit] = None
        self.__scripter__: typing.Optional[scriptercore.Scripter] = None
        self.__running__: bool = False
        self.__parameters__: typing.Dict[str, str] = {}
        self.__configure__: typing.Callable = lambda **kwargs: None

    @property
    def exploit(self) -> exploitcore.Exploit:
        return self.__exploit__

    @exploit.setter
    def exploit(self, sploit: exploitcore.Exploit) -> None:
        self.__exploit__ = sploit

    @property
    def scripter(self) -> scriptercore.Scripter:
        return self.__scripter__

    @scripter.setter
    def scripter(self, script: scriptercore.Scripter) -> None:
        self.__scripter__ = script

    @property
    def parameters(self) -> typing.Dict[str, str]:
        return self.__parameters__

    @property
    def configure(self) -> typing.Callable:
        return self.__configure__

    @configure.setter
    def configure(self, configfct: typing.Callable) -> None:
        self.__configure__ = configfct

    def customize(self, parameters: typing.Dict[str, str]) -> None:
        self.__parameters__ = parameters

    @abstractmethod
    def __send__(self, cmdline: str) -> None:
        pass

    @abstractmethod
    def __recv__(self, size: int) -> str:
        pass

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def run(self, exploit: exploitcore.Exploit, scripter: scriptercore.Scripter) -> None:
        pass


class AsynchronousBasicRemoteShell(Shell):
    __metaclass__ = ABCMeta

    AUTHOR: str = "Danakane"
    PDUMAXSIZE: int = 65535

    def __init__(self) -> None:
        Shell.__init__(self)
        self.__rhost__: str = ""
        self.__rport__: int = 0
        self.__lhost__: str = ""
        self.__lport__: int = 0
        self.__rsockaddr__: typing.Tuple[typing.Any, ...] = ()
        self.__lsockaddr__: typing.Tuple[typing.Any, ...] = ()
        self.__shellskt__: socket.socket = socket.socket()
        self.__protocol__: int = 0
        self.__recvthrd__: threading.Thread = threading.Thread()
        self.__lastcmd__: str = ""
        self.customize({"rhost": "", "rport": "", "lhost": "", "lport": ""})
        self.configure = self.__doconfig__

    @property
    def rhost(self) -> str:
        return self.__rhost__

    @property
    def lhost(self) -> str:
        return self.__lhost__

    @property
    def rport(self) -> int:
        return self.__rport__

    @property
    def lport(self) -> int:
        return self.__lport__

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
    def shellskt(self) -> socket.socket:
        return self.__shellskt__

    @shellskt.setter
    def shellskt(self, shellsock: socket.socket) -> None:
        self.__shellskt__ = shellsock

    def __send__(self, cmdline: str) -> None:
        self.__shellskt__.send(utils.str2bytes(cmdline) + b"\n")

    def __recv__(self, size: int) -> str:
        return utils.bytes2str(self.__shellskt__.recv(size))

    def __recvloop__(self) -> None:
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

    def __doconfig__(self, rhost: str, rport: str, lhost: str = "", lport: str = "0") -> None:
        self.__rhost__ = str(rhost)
        self.__rport__ = int(rport)
        self.__lhost__ = str(lhost)
        self.__lport__ = int(lport)
        self.__rsockaddr__ = ()
        self.__lsockaddr__ = ()
        self.__shellskt__ = socket.socket()
        self.__running__ = False
        self.__protocol__ = 0
        rsockinfo: typing.Tuple[int, int, int, str, typing.Tuple[typing.Any, ...]] \
            = netutils.getsockinfo(self.__rhost__, self.__rport__)
        self.__rsockaddr__ = rsockinfo[4]
        if self.__lhost__:
            lsockinfo = netutils.getsockinfo(self.__lhost__, self.__lport__)
            self.__lsockaddr__ = lsockinfo[4]
            self.__protocol__ = lsockinfo[0]
        else:
            self.__protocol__ = rsockinfo[0]

    def run(self, exploit: exploitcore.Exploit, scripter: scriptercore.Scripter) -> None:
        self.exploit = exploit
        self.scripter = scripter
        self.initialize()
        if self.scripter:
            self.scripter.execute(self.__shellskt__)
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
