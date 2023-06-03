// mapspawn.nut is called twice on map transitions for some reason...
// Prevent the second run

if (!("Entities" in this)) { return }

printl("calling p2mm===")

function ChatCommands(var1, var2) {
    SendToChat("entindex " + var1.tostring(), 0)
    SendToChat("message " + var2.tostring(), 0)
}

function Plyr_Disconnect_Function() {
    printl("You are gay?")
}

IncludeScript("modules/loop.nut")