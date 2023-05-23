logs = {
    "global":[]
}

logfilepath = "p2mm.log"
logfile = open(logfilepath, "w", encoding="utf-8")

def log(text, type = "primary", shouldprint = True):
    global logfile

    if type not in logs.keys():
        logs[type] = []

    text = str(text)
    logs[type].append(text)
    logs["global"].append([type, text])
    
    logfile.write(type + ": " + text + "\n")

    if shouldprint:
        print(type + ": " + text)


def getnewlines(linenum, loglevel = "global"): # this is a simple way for modules to request a log update
    newnum = len(logs[loglevel])
    if linenum == newnum:
        return [[], newnum]
    newlines = logs[loglevel][linenum:newnum]
    
    if loglevel == "global": # format the global log correctly if nessacary
        newnewlines = []
        for line in newlines:
            newnewlines.append(line[0] + ": " + line[1])
        newlines = newnewlines

    return [newlines, newnum]