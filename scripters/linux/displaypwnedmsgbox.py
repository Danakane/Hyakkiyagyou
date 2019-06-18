import typing

from core import scriptercore


class LinuxDisplayPwnedMsgBox(scriptercore.Scripter):

    AUTHOR: str = "Danakane"

    def __init__(self):
        super(LinuxDisplayPwnedMsgBox, self).__init__()
        self.__title__: str = ""
        self.__text__: str = ""
        self.customize({"title": "The title of the messagebox",
                        "text": "The message of the messagebox"})
        self.configure = self.__doconfig__

    def __doconfig__(self, title, text):
        self.__title__ = title
        self.__text__ = text

    def dojob(self) -> None:
        self.send(str.format("zenity --error --text {0} --title {1} --width=200&",
                             self.__text__, self.__title__))


blueprint: typing.Callable = LinuxDisplayPwnedMsgBox
