import typing
from pytoolcore import style, netutils, exception, command, engine
from core import blueprintregister, exploitcore, payloadcore, shellcore, scriptercore
from shells import shellsindex


class Matoi(engine.Engine):
    MODNAME: str = "Matoi"
    AUTHOR: str = "Danakane"

    DEFAULTSHELL: str = shellsindex.ShellsIndex.basicreuse

    def __init__(self, parentref: str, parentname: str, exploitref: str, exploit: exploitcore.Exploit,
                 shellreg: blueprintregister.ShellRegister,
                 payloadreg: blueprintregister.PayloadRegister,
                 scripterreg: blueprintregister.ScripterRegister) -> None:
        moduleref: str = parentref + "(" + style.Style.bold(style.Style.red(exploitref)) + ")"
        super(Matoi, self).__init__(moduleref=moduleref,
                                    modulename=exploitref,
                                    author=type(exploit).AUTHOR)
        self.__parentname__: str = parentname
        self.__exploit__: exploitcore.Exploit = exploit
        self.__shellreg__: blueprintregister.ShellRegister = shellreg
        self.__payloadreg__: blueprintregister.PayloadRegister = payloadreg
        self.__scripterreg__: blueprintregister.ScripterRegister = scripterreg

        # Defining the Matoi's variables
        self.addvar(varname="PAYLOAD",
                    description="The payload to use",
                    settable=True, value="")

        self.addvar(varname="SCRIPTER",
                    description="The post-exploitation script to use",
                    settable=True, value="")

        self.addvar(varname="TARGET",
                    description="The target of the exploit",
                    settable=True, value="")

        self.addvar(varname="LHOST",
                    description="The local host name or address",
                    settable=True, value="")

        self.addvar(varname="LPORT",
                    description="The local host port number to use",
                    settable=True, value="")

        self.addvar(varname="RHOST",
                    description="The remote host name or address",
                    settable=True, value="")

        self.addvar(varname="RPORT",
                    description="The remote host port number to use",
                    settable=True, value="")

        # Defining the module's commands
        # set command
        cmdset: command.Command = command.Command(cmdname="set", nbpositionals=2,
                                                  completionlist=list(self.__dictvar__.keys()))
        sethelp: str = "Description : set a variable with a value\n" + \
                       "Usage : set {variable} {value}\n" + \
                       "Note : use 'show options' " + \
                       "to display settable variable"
        self.addcmd(cmd=cmdset, fct=self.set, helpstr=sethelp)

        # show command
        cmdshow: command.Command = command.Command(cmdname="show", nbpositionals=1,
                                                   completionlist=["commands", "name",
                                                                   "author", "options", "payloads",
                                                                   "scripters"])
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

        # pwn command
        argpayload: command.Argument = command.Argument(argname="payload", hasvalue=True, optional=True)
        argscripter: command.Argument = command.Argument(argname="scripter", hasvalue=True, optional=True)
        argtarget: command.Argument = command.Argument(argname="target", hasvalue=True, optional=True)
        arglhost: command.Argument = command.Argument(argname="lhost", hasvalue=True, optional=True)
        arglport: command.Argument = command.Argument(argname="lport", hasvalue=True, optional=True)
        argrhost: command.Argument = command.Argument(argname="rhost", hasvalue=True, optional=True)
        argrport: command.Argument = command.Argument(argname="rport", hasvalue=True, optional=True)
        pwnargs = [argpayload, argscripter, argtarget, arglhost, arglport, argrhost, argrport]
        cmdpwn: command.Command = command.Command(cmdname="pwn", nargslist=pwnargs, nbpositionals=0)
        pwnhelp: str = "Description : pwn " + self.__modulename__ + \
                       " exploit with the given parameters\n" + \
                       "Usage : pwn [option][value] \n" + \
                       "Options list : payload, lhost, lport, " + \
                       "rhost, rport\n" + \
                       "Note : \n" + \
                       "\toption payload : the payload to use\n" + \
                       "\toption lhost : local host\n" + \
                       "\toption lport : local host port number to use\n" + \
                       "\toption rhost : remote host\n" + \
                       "\toption rport : remote host target port number\n" + \
                       "Example : pwn payload reverse/linux_netcat " + \
                       "rhost 192.168.1.92 rport 1025 " + \
                       "lhost 192.168.1.84 lport 5555"
        self.addcmd(cmd=cmdpwn, fct=self.pwn, helpstr=pwnhelp)

    def set(self, varname, value) -> None:
        varname = varname.upper()
        if "PORT" in varname:
            if int(value) not in range(1, 65536):
                raise ValueError("Invalid port number " + value)
            self.setvar(varname=varname, value=value)
        elif "PAYLOAD" == varname:
            if value in self.__payloadreg__.list:
                self.setvar(varname=varname, value=value)
            else:
                raise ValueError(value + " is not a compatible payload for a payload")
        elif "SCRIPTER" == varname:
            if value in self.__scripterreg__.list:
                self.setvar(varname=varname, value=value)
            else:
                raise ValueError(value + " is not a script")
        elif "TARGET" == varname:
            if value in self.__exploit__.targets:
                self.setvar(varname=varname, value=value)
            else:
                raise ValueError(value + " is not a valid target for " + self.modulename)
        else:
            self.setvar(varname=varname, value=value)

    def show(self, keyword: str) -> None:
        keyword = keyword.upper()
        if keyword == "PAYLOADS":
            payloadlist: typing.List[str] = self.__exploit__.comploads
            availableploads: typing.List[str] = self.__payloadreg__.list
            print(style.Style.info(self.modulename + " compatible payloads"))
            for payloadref in payloadlist:
                if payloadref in availableploads:
                    print(payloadref)
        elif keyword == "SCRIPTERS":
            scripterlist: typing.List[str] = self.__scripterreg__.list
            print(style.Style.info(self.__parentname__ + "'s post-exploitation scripts"))
            for scripterref in scripterlist:
                print(scripterref)
        elif keyword == "TARGETS":
            targetslist: typing.List[str] = self.__exploit__.targets
            print(style.Style.info(self.modulename + "'s targets"))
            for targetref in targetslist:
                print(targetref)
        else:
            super(Matoi, self).show(keyword)

    def pwn(self, payload: str = "", scripter: str = "", target: str = "",
            lhost: str = "", lport: str = "", rhost: str = "", rport: str = "") -> None:
        rportstr: str = rport
        lportstr: str = lport
        payloadref: str = payload
        scripterref: str = scripter
        if not payloadref:
            payloadref = self.getvar("PAYLOAD")
        if not scripterref:
            scripterref = self.getvar("SCRIPTER")
        if not target:
            target = self.getvar("TARGET")
        if not lhost:
            lhost = self.getvar("LHOST")
        if not lportstr:
            lportstr = self.getvar("LPORT")
        if not rhost:
            rhost = self.getvar("RHOST")
            if not rhost:
                raise ValueError("No remote host provided.")
        if not rportstr:
            rportstr = self.getvar("RPORT")
            if not rportstr:
                raise ValueError("No remote port provided")

        rhost = netutils.gethostaddrbyname(rhost)
        if lhost:
            lhost = netutils.gethostaddrbyname(lhost)

        rport: int = int(rportstr)
        lport: int = 0
        if lportstr:
            lport = int(lportstr)

        payload: typing.Optional[payloadcore.Payload] = None
        if payloadref is not None and payloadref != "":
            payload = self.__payloadreg__[payloadref]()
            payload.setup(lhost, lport)
        exploit: exploitcore.Exploit = self.__exploit__.generate(payload, target)
        scripter: typing.Optional[scriptercore.Scripter] = None
        try:
            if scripterref != "":
                scripter = self.__scripterreg__[scripterref]()
        except KeyError:
            print(style.Style.warning("Invalid post-exploitation script " + scripterref))
        kwargs: typing.Dict[str, typing.Any] = {"exploit": exploit, "scripter": scripter,
                                                "rhost": rhost, "rport": rport,
                                                "lhost": lhost, "lport": lport}
        shellref: str = Matoi.DEFAULTSHELL
        if payload and payload.shellref:
            shellref = payload.shellref
        shell: shellcore.RemoteShell = self.__shellreg__[shellref]()

        try:
            shell.run(**kwargs)
        except OSError as err:
            raise (exception.ErrorException(str(err)))

    def completer(self, text: str, state: int) -> str:
        subtext: str = text.split(" ")[-1].lower()
        if len(text.split(" ")) > 2 and text.split(" ")[-2].lower() == "payload":
            wordslist: typing.List[str] = self.__payloadreg__.list
            retlist: typing.List[str] = text.split(" ")[:-1]
            retlist.append([x for x in wordslist if x.lower().startswith(subtext, 0) and
                            x.lower() not in text.lower().split(" ") and
                            (subtext.strip() != "")][state])
            res: str = " ".join(retlist)
        elif len(text.split(" ")) > 2 and text.split(" ")[-2].lower() == "scripter":
            wordslist: typing.List[str] = self.__scripterreg__.list
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
