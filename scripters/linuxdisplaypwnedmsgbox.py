import typing

from core import scriptercore


class LinuxDisplayPwnedMsgBox(scriptercore.Scripter):

    SCRIPTERREF: str = "linux_displaypwnedmsgbox"
    AUTHOR: str = "Danakane"

    def __init__(self):
        super(LinuxDisplayPwnedMsgBox, self).__init__(ref=LinuxDisplayPwnedMsgBox.SCRIPTERREF,
                                                      author=LinuxDisplayPwnedMsgBox.AUTHOR)
        pass

    def execute(self) -> None:
        self.send("zenity --error --text 'You have been pwned :)' --title 'Oh crap!' --width=200&")


blueprint: typing.Callable = LinuxDisplayPwnedMsgBox
name: str = LinuxDisplayPwnedMsgBox.SCRIPTERREF

