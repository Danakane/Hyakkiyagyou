import pathlib
import typing
import importlib.util


class BlueprintRegister:

    def __init__(self, path: str)->None:
        self.__blueprintspath__: pathlib.Path = pathlib.Path(path).absolute()
        self.__blueprintsdict__: typing.Dict[str, typing.Callable] = {}
        for file in self.__blueprintspath__.iterdir():
            if file.is_file() and not file.is_symlink():
                try:
                    spec: importlib.util.spec_from_file_location = importlib.util.spec_from_file_location(
                        file.name.split(".")[0], file)
                    mod: importlib.util.module_from_spec = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    self.__blueprintsdict__[mod.name] = mod.blueprint
                except AttributeError:
                    pass

    def __getitem__(self, index: str)->typing.Callable:
        return self.__blueprintsdict__[index]

    def addblueprint(self, name: str, blueprint: typing.Callable)->None:
        try:
            self.removeblueprint(name)
        except KeyError:
            pass
        self.__blueprintsdict__[name] = blueprint

    def removeblueprint(self, name)->None:
        del self.__blueprintsdict__[name]

    @property
    def list(self)->typing.List[str]:
        return list(self.__blueprintsdict__.keys())


class ShellRegister(BlueprintRegister):

    def __init__(self, relativepath: str="./shells")->None:
        super(ShellRegister, self).__init__(relativepath)

    def addshell(self, shellname: str, shellclass: typing.Callable)->None:
        self.addblueprint(shellname, shellclass)

    def removeshell(self, shellname: str)->None:
        self.removeblueprint(shellname)


class PayloadRegister(BlueprintRegister):

    def __init__(self, relativepath: str="./payloads")->None:
        super(PayloadRegister, self).__init__(relativepath)

    def addpayloadclass(self, payloadref: str, payloadclass: typing.Callable)->None:
        self.addblueprint(payloadref, payloadclass)

    def removeshell(self, payloadref: str)->None:
        self.removeblueprint(payloadref)


class ExploitRegister(BlueprintRegister):

    def __init__(self, relativepath: str="./exploits")->None:
        super(ExploitRegister, self).__init__(relativepath)

    def addexploitclass(self, exploitref: str, exploitclass: typing.Callable)->None:
        self.addblueprint(exploitref, exploitclass)

    def removeshell(self, exploitref: str)->None:
        self.removeblueprint(exploitref)


class ModuleRegister(BlueprintRegister):
    def __init__(self, relativepath: str=".")->None:
        super(ModuleRegister, self).__init__(relativepath)

    def addexploitclass(self, moduleref: str, moduleclass: typing.Callable)->None:
        self.addblueprint(moduleref, moduleclass)

    def removeshell(self, moduleref: str)->None:
        self.removeblueprint(moduleref)
