import typing
from pytoolcore import style, exception, command, engine
from core import factory, exploitcore, payloadcore, shellcore, scriptercore
from shells import shellsindex


class Matoi(engine.Engine):
    MODNAME: str = "Matoi"
    AUTHOR: str = "Danakane"

    DEFAULTSHELL: str = shellsindex.ShellsIndex.basicreuse

    def __init__(self, parentref: str, parentname: str, exploitref: str, exploit: exploitcore.Exploit,
                 shellfactory: factory.ShellFactory,
                 payloadfactory: factory.PayloadFactory,
                 scripterfactory: factory.ScripterRegister) -> None:
        moduleref: str = "{0}({1})".format(parentref, style.Style.bold(style.Style.red(exploitref)))
        super(Matoi, self).__init__(moduleref=moduleref,
                                    modulename=exploitref,
                                    author=type(exploit).AUTHOR)
        self.__parentname__: str = parentname
        self.__exploit__: exploitcore.Exploit = exploit
        self.__shellfactory__: factory.ShellFactory = shellfactory
        self.__payloadfactory__: factory.PayloadFactory = payloadfactory
        self.__scripterfactory__: factory.ScripterRegister = scripterfactory
        # Defining the Matoi's variables
        self.addoption(optname="payload", description="The payload to use", value="")
        self.addoption(optname="scripter", description="The post-exploitation script to use", value="")
        # Defining the module's commands
        self.__updatecommands__()

    def __updatecommands__(self):
        pwnhelp: str = "Description : pwn " + self.__modulename__ + \
                       " exploit with the given parameters\n" + \
                       "Usage : pwn [option][value] \n" + \
                       "Options list : use show options to display options"
        pwnargs: typing.List[command.Argument] = []
        # add exploit parameters
        for arg, desc in self.__exploit__.parameters.items():
            if arg not in self.getoptnames():
                self.addoption(arg, desc)
            pwnargs.append(command.Argument(argname=arg, hasvalue=True, optional=True))
        # add payload parameters
        payloadref: str = self.getoptionvalue("payload")
        if payloadref:
            payload: payloadcore.Payload = self.__payloadfactory__[payloadref]()
            for arg, desc in payload.parameters.items():
                if arg not in self.getoptnames():
                    self.addoption(arg, desc)
                pwnargs.append(command.Argument(argname=arg, hasvalue=True, optional=True))
        # add scripter parameters
        scripterref: str = self.getoptionvalue("scripter")
        if scripterref:
            scripter: scriptercore.Scripter = self.__scripterfactory__[scripterref]()
            for arg, desc in scripter.parameters.items():
                if arg not in self.getoptnames():
                    self.addoption(arg, desc)
                pwnargs.append(command.Argument(argname=arg, hasvalue=True, optional=True))
        cmdpwn: command.Command = command.Command(cmdname="pwn", nargslist=pwnargs, nbpositionals=0)
        self.addcmd(cmdpwn, self.pwn, pwnhelp)
        # set command
        cmdset: command.Command = command.Command(cmdname="set", nbpositionals=2,
                                                  completionlist=self.getoptnames())
        sethelp: str = "Description : set a variable with a value\n" + \
                       "Usage : set {variable} {value}\n" + \
                       "Note : use 'show options' " + \
                       "to display settable variable"
        self.addcmd(cmd=cmdset, fct=self.set, helpstr=sethelp)
        # reset command
        resethelp: str = "Description : reset a variable\n" + \
                         "Usage : reset {options}\n" + \
                         "Note : Use 'show options' to display available options"
        cmdreset: command.Command = command.Command(cmdname="reset", nbpositionals=1,
                                                    completionlist=self.getoptnames())
        self.addcmd(cmd=cmdreset, fct=self.reset, helpstr=resethelp)
        # show command
        cmdshow: command.Command = command.Command(cmdname="show", nbpositionals=1,
                                                   completionlist=["commands", "name",
                                                                   "author", "options", "payloads",
                                                                   "scripters", "targets"] + self.getoptnames())
        showhelp: str = "Description : display option(s), command(s) and attack(s)\n" + \
                        "Usage : show {keyword} \n" + \
                        "Note :\n" + \
                        "\tuse 'show name' to display module's name\n" + \
                        "\tuse 'show author' to display module's author\n" + \
                        "\tuse 'show commands' to display the module's commands\n" + \
                        "\tuse 'show payloads' to display the available payloads\n" + \
                        "\tuse 'show scripters' to display the available post-exploitation scripts\n" + \
                        "\tuse 'show targets' to display the possible targets of the exploit\n" + \
                        "\tuse 'show options' to display valid keywords\n"
        self.addcmd(cmd=cmdshow, fct=self.show, helpstr=showhelp)

    def set(self, optname: str, value: str, verbose: bool = True) -> None:
        optname = optname.lower()
        if "payload" == optname:
            if value in self.__payloadfactory__.list or not value:
                payloadref: str = self.getoptionvalue("payload")
                if payloadref:
                    payload: payloadcore.Payload = self.__payloadfactory__[payloadref]()
                    for opt in payload.parameters:
                        toremove: bool = True
                        if opt in self.__exploit__.parameters:
                            toremove = False
                        scripterref: str = self.getoptionvalue("scripter")
                        if scripterref and opt in self.__scripterfactory__[scripterref]().parameters:
                            toremove = False
                        if toremove:
                            self.removeoption(opt)
                self.setvar(optname=optname, value=value, verbose=verbose)
            else:
                raise ValueError(value + " is not a compatible payload for a payload")
        elif "scripter" == optname:
            if value in self.__scripterfactory__.list or not value:
                scripterref: str = self.getoptionvalue("scripter")
                if scripterref:
                    scripter: scriptercore.Scripter = self.__scripterfactory__[scripterref]()
                    for opt in scripter.parameters:
                        toremove: bool = True
                        if opt in self.__exploit__.parameters:
                            toremove = False
                        payloadref: str = self.getoptionvalue("payload")
                        if payloadref and opt in self.__payloadfactory__[payloadref]().parameters:
                            toremove = False
                        if toremove:
                            self.removeoption(opt)
                self.setvar(optname=optname, value=value, verbose=verbose)
            else:
                raise ValueError(value + " is not a script")
        elif "target" == optname:
            if value in self.__exploit__.targets or not value:
                self.setvar(optname=optname, value=value, verbose=verbose)
            else:
                raise ValueError(value + " is not a valid target for " + self.modulename)
        else:
            self.setvar(optname=optname, value=value, verbose=verbose)
        self.__updatecommands__()

    def reset(self, optname) -> None:
        optname = optname.lower()
        if optname == "all" or optname == "*":
            for option in self.getoptnames():
                self.set(option, "", False)
        else:
            self.set(optname, "", False)

    def show(self, keyword: str) -> None:
        table: typing.List[typing.List[str]] = []
        keyword = keyword.lower()
        if keyword == "options":
            headers: typing.List[str] = ["Option", "Current setting", "Description"]
            table: typing.List[typing.List[str]] = []
            # print exploit's parameters
            print(style.Style.info("Exploit's parameters"))
            table.append(["payload", self.getoptionvalue("payload"), self.getoptiondesc("payload")])
            table.append(["scripter", self.getoptionvalue("scripter"), self.getoptiondesc("scripter")])
            for optname in self.getoptnames():
                if optname in self.__exploit__.parameters:
                    table.append([optname, self.getoptionvalue(optname), self.getoptiondesc(optname)])
            print(style.Style.tabulate(headers, table))
            print()
            table = []
            # print payload parameters if needed
            payloadref: str = self.getoptionvalue("payload")
            if payloadref:
                print(style.Style.info("Payload's parameters"))
                payload: payloadcore.Payload = self.__payloadfactory__[payloadref]()
                for optname in self.getoptnames():
                    if optname in payload.parameters:
                        table.append([optname, self.getoptionvalue(optname), self.getoptiondesc(optname)])
                print(style.Style.tabulate(headers, table))
                print()
                table = []
            # print scripter parameters if needed
            scripterref: str = self.getoptionvalue("scripter")
            if scripterref:
                print(style.Style.info("Scripter's parameters"))
                scripter: scriptercore.Scripter = self.__scripterfactory__[scripterref]()
                for optname in self.getoptnames():
                    if optname in scripter.parameters:
                        table.append([optname, self.getoptionvalue(optname), self.getoptiondesc(optname)])
                print(style.Style.tabulate(headers, table))
                print()
        elif keyword == "payloads":
            headers: typing.List[str] = ["Payload", "Author"]
            payloadlist: typing.List[str] = self.__exploit__.comploads
            availableploads: typing.List[str] = self.__payloadfactory__.list
            print(style.Style.info("{0}'s compatible payloads".format(self.modulename)))
            for payloadref in payloadlist:
                if payloadref in availableploads:
                    # noinspection PyUnresolvedReferences
                    table.append([payloadref, self.__payloadfactory__[payloadref].AUTHOR])
            print(style.Style.tabulate(headers, table, True))
            print()
        elif keyword == "scripters":
            headers: typing.List[str] = ["Scripter", "Author"]
            scripterlist: typing.List[str] = self.__scripterfactory__.list
            print(style.Style.info("{0}'s post-exploitation scripts".format(self.__parentname__)))
            for scripterref in scripterlist:
                # noinspection PyUnresolvedReferences
                table.append([scripterref, self.__scripterfactory__[scripterref].AUTHOR])
            print(style.Style.tabulate(headers, table, True))
            print()
        elif keyword == "targets":
            targetslist: typing.List[str] = self.__exploit__.targets
            print(style.Style.info("{0}'s targets".format(self.modulename)))
            if targetslist:
                headers: typing.List[str] = ["Target"]
                for targetref in targetslist:
                    table.append([targetref])
                print(style.Style.tabulate(headers, table, True))
                print()
            else:
                print("No specific target")
        else:
            super(Matoi, self).show(keyword)

    def pwn(self, **kwargs) -> None:
        # add exploits parameters
        exploitparameters: typing.Dict[str, str] = {}
        # add command line arguments
        for kwarg in kwargs:
            if kwarg in self.__exploit__.parameters:
                exploitparameters[kwarg] = kwargs[kwarg]
        # add parameters from options if missing
        for kwarg in self.__exploit__.parameters:
            if kwarg not in exploitparameters:
                exploitparameters[kwarg] = self.getoptionvalue(kwarg)
        # add payload parameters
        payloadparameters: typing.Dict[str, str] = {}
        payloadref: str = self.getoptionvalue("payload")
        if payloadref:
            parameters: typing.List[str] = self.__payloadfactory__[payloadref]().parameters
            for kwarg in kwargs:
                if kwarg in parameters:
                    payloadparameters[kwarg] = kwargs[kwarg]
            # add parameters from options if missing
            for kwarg in parameters:
                if kwarg not in payloadparameters:
                    payloadparameters[kwarg] = self.getoptionvalue(kwarg)
        # add scripter parameters
        scripterparameters: typing.Dict[str, str] = {}
        scripterref: str = self.getoptionvalue("scripter")
        if scripterref:
            parameters: typing.List[str] = self.__scripterfactory__[scripterref]().parameters
            for kwarg in kwargs:
                if kwarg in parameters:
                    scripterparameters[kwarg] = kwargs[kwarg]
            # add parameters from options if missing
            for kwarg in parameters:
                if kwarg not in scripterparameters:
                    scripterparameters[kwarg] = self.getoptionvalue(kwarg)
        # generate payload
        payload: typing.Optional[payloadcore.Payload] = None
        try:
            if payloadref:
                payload = self.__payloadfactory__[payloadref]()
                payload.configure(**payloadparameters)
        except EnvironmentError as err:
            raise (exception.ErrorException(str(err)))
        # generate exploit
        try:
            exploit: exploitcore.Exploit = self.__exploit__.generate(payload, exploitparameters)
        except EnvironmentError as err:
            raise (exception.ErrorException(str(err)))
        # generate scripter
        scripter: typing.Optional[scriptercore.Scripter] = None
        try:
            if scripterref:
                scripter = self.__scripterfactory__[scripterref]()
                scripter.configure(**scripterparameters)
        except EnvironmentError as err:
            raise (exception.ErrorException(str(err)))
        # generate shell
        try:
            shellref: str = Matoi.DEFAULTSHELL
            if payload and payload.shellref:
                shellref = payload.shellref
            shell: shellcore.Shell = self.__shellfactory__[shellref]()
            shellparameters: typing.Dict[str, str] = {}
            for kwarg in kwargs:
                if kwarg in shell.parameters:
                    shellparameters[kwarg] = kwargs[kwarg]
            for kwarg in shell.parameters:
                if kwarg not in shellparameters:
                    shellparameters[kwarg] = self.getoptionvalue(kwarg)
            shell.configure(**shellparameters)
        except EnvironmentError as err:
            raise (exception.ErrorException(str(err)))
        # pwn
        try:
            shell.run(exploit, scripter)
        except EnvironmentError as err:
            raise (exception.ErrorException(str(err)))
        return

    def completer(self, text: str, state: int) -> str:
        subtext: str = text.split(" ")[-1].lower()
        if len(text.split(" ")) > 2 and text.split(" ")[-2].lower() == "payload":
            wordslist: typing.List[str] = self.__exploit__.comploads
            retlist: typing.List[str] = text.split(" ")[:-1]
            retlist.append([x for x in wordslist if x.lower().startswith(subtext, 0) and
                            x.lower() not in text.lower().split(" ") and
                            (subtext.strip() != "")][state])
            res: str = " ".join(retlist)
        elif len(text.split(" ")) > 2 and text.split(" ")[-2].lower() == "scripter":
            wordslist: typing.List[str] = self.__scripterfactory__.list
            retlist: typing.List[str] = text.split(" ")[:-1]
            retlist.append([x for x in wordslist if x.lower().startswith(subtext, 0) and
                            x.lower() not in text.lower().split(" ") and
                            (subtext.strip() != "")][state])
            res: str = " ".join(retlist)
        elif len(text.split(" ")) > 2 and text.split(" ")[-2].lower() == "target":
            wordslist: typing.List[str] = self.__exploit__.targets
            retlist: typing.List[str] = text.split(" ")[:-1]
            retlist.append([x for x in wordslist if x.lower().startswith(subtext, 0) and
                            x.lower() not in text.lower().split(" ") and
                            (subtext.strip() != "")][state])
            res: str = " ".join(retlist)
        else:
            res: str = super(Matoi, self).completer(text, state)
        return res
