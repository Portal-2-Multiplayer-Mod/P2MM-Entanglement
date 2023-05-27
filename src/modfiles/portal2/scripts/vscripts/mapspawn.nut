printl("==== calling p2mm")

lastmessage <- ""

function ChatCommands(var1, var2) {
    SendToChat("entindex " + var1.tostring(), 0)
    SendToChat("message " + var2.tostring(), 0)
    lastmessage = var2.tostring()
}

function returnsomedata() {
    printl(lastmessage)
}