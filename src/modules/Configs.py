from enum import Enum
import os
import modules.functions as fn
#! do not touch the config model
#! do not call any function / variable that starts with "__" outside of this file


class ConfigModel():
    Label: str
    Type: type
    Hint: str
    __Value: any

    def __init__(self, label: str, type: type, hint: str, defaultValue: any):
        self.Label = label
        self.Type = type
        self.Hint = hint
        self.SetValue(defaultValue)

    def SetValue(self, value: any) -> None:
        value = fn.ConvertValue(value, self.Type)
        if value is None:
            raise TypeError(f"cannot convert {type(value)} to {self.Type}")
        self.__Value = value

    def GetValue(self) -> any:
        return self.__Value


class Configs(Enum):
    GamePath = "GamePath"
    CheckUpdateOnStart = "CheckUpdateOnStart"


__defaultConfig: dict[Configs, ConfigModel] = {
    Configs.GamePath:
        ConfigModel("portal 2 path", str, "the folder where p2 is installed",
                    "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Portal 2"),
    Configs.CheckUpdateOnStart:
        ConfigModel("do you want to check for updates on start up?", bool,
                    "if enabled checks for update when the launcher opens", True)
}

Data: dict[Configs, ConfigModel] = __defaultConfig


def __CreateNewConfigFile():
    configs: list[str] = []

    for config in Configs:
        configs.append(f"{config.value} = {GetDefaultValue(config)}\n")

    fn.WriteToFile(__GetConfigFilePath(), configs)


def LoadConfigs():
    #! ONLY CALLED ONCE IN MAIN

    if not os.path.exists(__GetConfigFilePath()):
        __CreateNewConfigFile()
        return

    data: list[str] = fn.ReadFile(__GetConfigFilePath()).split("\n")

    if data is None:
        __CreateNewConfigFile()
        return

    for line in data:
        line = line.strip().split("=")
        config = __GetEnumByName(line[0].strip())
        if config is None:
            continue
        Data[config].SetValue(line[1].strip())

def __GetEnumByName(name:str) -> Configs | None:
    for enum in Configs:
        if enum.value == name:
            return enum
    return None

def __SaveConfigs():
    configs: list[str] = []

    for config in Configs:
        configs.append(f"{config.value} = {GetValue(config)}\n")

    fn.WriteToFile(__GetConfigFilePath(), configs)


def __GetConfigFilePath() -> str:
    return "config.cfg"


def GetDefaultValue(config: Configs) -> any:
    return __defaultConfig[config].GetValue()


def GetValue(config: Configs) -> any:
    return Data[config].GetValue()


def SetValue(config: Configs, value: any) -> None:
    Data[config].SetValue(value)
    __SaveConfigs()

