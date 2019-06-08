import typing

from pytoolcore import style
from core import exploitcore, shellcore, scriptercore


class BasicReuseShell(shellcore.AsynchronousBasicRemoteShell):

    SHELLREF: str = "BasicReuseShell"

    def __init__(self, exploit: exploitcore.Exploit, scripter: scriptercore.Scripter, rhost, rport)->None:
        if rhost and rport:
            shellcore.AsynchronousBasicRemoteShell.__init__(self, exploit=exploit, scripter=scripter,
                                                            rhost=rhost, rport=rport)
        else:
            raise ValueError("Missing or incorrect parameters")

    def initialize(self)->None:
        self.shellskt = self.exploit.run(self.rsockaddr)
        self.__send__("whoami")
        self.__recv__(shellcore.AsynchronousBasicRemoteShell.PDUMAXSIZE)
        print(style.Style.success("You have control! :)"))


blueprint: typing.Callable = BasicReuseShell
name: str = BasicReuseShell.SHELLREF
