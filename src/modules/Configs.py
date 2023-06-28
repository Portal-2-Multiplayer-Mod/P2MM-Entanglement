from enum import Enum
import os
import modules.functions as fn

#! do not call any function / variable that starts with "__" outside of this file


class ConfigProperties(Enum):
    GamePath = "GamePath"
    CheckUpdateOnStart = "CheckUpdateOnStart"
    Timeout = "Timeout"


class ConfigModel():
    Label: str
    Type: type
    Hint: str

    def __init__(self, label: str, type: type, hint: str):
        self.Label = label
        self.Type = type
        self.Hint = hint


ConfigsModels: dict[ConfigProperties, ConfigModel] = {
    ConfigProperties.GamePath:
        ConfigModel("portal 2 path", str, "the folder where p2 is installed"),

    ConfigProperties.CheckUpdateOnStart:
        ConfigModel("do you want to check for updates on start up?",
                    bool, "if enabled checks for update when the launcher opens"),

    ConfigProperties.Timeout:
        ConfigModel("timeout?",
                    int, "timeout :D"),
}

DefaultData: dict[ConfigProperties, any] = {
    ConfigProperties.GamePath: "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Portal 2",
    ConfigProperties.CheckUpdateOnStart: True,
    ConfigProperties.Timeout: 2,
}

UserData: dict[ConfigProperties, any] = DefaultData


def LoadConfigs() -> None:
    #! ONLY CALLED ONCE IN MAIN

    if not os.path.exists(__GetConfigsFilePath()):
        __SaveConfigs(DefaultData)
        return

    data: list[str] = fn.ReadFile(__GetConfigsFilePath()).split("\n")
    errors = 0

    for line in data:
        line = line.strip().split("=")
        config = __GetEnumByName(line[0].strip())
        if config is None or line[1].strip() == "":
            errors += 1
            continue
        SetValue(config, line[1].strip(), False)

    if errors > 0:
        __SaveConfigs()


def __GetEnumByName(name: str) -> ConfigProperties | None:
    for enum in ConfigProperties:
        if enum.value == name:
            return enum
    return None


def __SaveConfigs(data: dict[ConfigProperties, any] = UserData) -> None:
    configs: list[str] = []

    for config in ConfigProperties:
        configs.append(f"{config.value} = {GetValue(config, data)}\n")

    fn.WriteToFile(__GetConfigsFilePath(), configs)


def __GetConfigsFilePath() -> str:
    return "config.cfg"


def GetValue(config: ConfigProperties, data=UserData) -> any:
    return data[config]

def GetDefaultValue(config: ConfigProperties) -> any:
    return DefaultData[config]

def GetLabelName(config: ConfigProperties) -> str:
    return ConfigsModels[config].Label

def GetHint(config: ConfigProperties) -> str:
    return ConfigsModels[config].Hint

def GetType(config: ConfigProperties) -> type:
    return ConfigsModels[config].Type


def SetValue(config: ConfigProperties, value: any, shouldSave: bool = True) -> None:
    try:
        value = fn.ConvertValue(value, GetType(config))
        if value is None:
            # todo: global error handler and an error popup
            raise TypeError(f"cannot convert {type(value)} to {GetType(config)}")

        UserData[config] = value
    except:
        UserData[config] = GetDefaultValue(config)

    if shouldSave:
        __SaveConfigs()