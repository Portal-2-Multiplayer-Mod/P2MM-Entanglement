Logs = {"global": []}

LogFilePath = "p2mm.log"


def log(text: str, type: str = "primary", shouldPrint: bool = True):
    """Custom logging function for P2MM

    Parameters
    ----------
    text : str
        the text to be logged
    type : str, optional
        the type of the log (primary, second etc...), by default "primary"
    shouldPrint : bool, optional
        should it be printed to screen?, by default True
    """
    if type not in Logs.keys():
        Logs[type] = []

    Logs[type].append(str(text))
    Logs["global"].append([type, text])

    #! Always use "with open" when dealing with files
    with open(LogFilePath, "a", encoding="utf-8") as logFile:
        logFile.write(type + ": " + text + "\n")

    if shouldPrint:
        print(type + ": " + text)


# this is a simple way for modules to request a log update
def GetNewLines(lineNum: int, logLevel: str = "global") -> tuple[list[str], int]:
    """returns the new lines from log

    Parameters
    ----------
    lineNum : int
        current line number you have
    logLevel : str, optional
        by default "global"

    Returns
    -------
    tuple[list[str], int]
        the new lines and how many lines in total there are
    """
    logLength = len(Logs[logLevel])
    if lineNum == logLength:
        return [[], logLength]

    newLines = Logs[logLevel][lineNum:logLength]

    if logLevel == "global":  # format the global log correctly if nessacary
        formattedLines = []
        for line in newLines:
            formattedLines.append(line[0] + ": " + line[1])
        newLines = formattedLines

    return (newLines, logLength)
