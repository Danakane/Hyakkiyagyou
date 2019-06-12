import typing

from core import scriptercore


class LinuxDisplayPwnedMsgBox(scriptercore.Scripter):

    AUTHOR: str = "Danakane"
    SCRIPTERREF: str = "linux_displaypwnedmsgbox"

    def __init__(self):
        super(LinuxDisplayPwnedMsgBox, self).__init__()
        self.customize(LinuxDisplayPwnedMsgBox.AUTHOR, LinuxDisplayPwnedMsgBox.SCRIPTERREF)

    def execute(self) -> None:
        self.send("zenity --error --text 'You have been pwned :)' --title 'Oh crap!' --width=200&")


blueprint: typing.Callable = LinuxDisplayPwnedMsgBox
name: str = LinuxDisplayPwnedMsgBox.SCRIPTERREF
