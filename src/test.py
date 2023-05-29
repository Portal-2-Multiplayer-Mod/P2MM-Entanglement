from rcon.source import Client
import netifaces, time

foundip = False
ip = ""

def sendrcon(cmd, password, addr, port = 3280, hist = False):
        with Client(addr, port, passwd=password) as client:
            response = client.run(cmd)
        return response

while not foundip:
    for interface in netifaces.interfaces():
        ifaddr = netifaces.ifaddresses(interface)
        if len(ifaddr) < 2: continue # if it doesn't include a ipv4 skip
        if 2 not in ifaddr: continue # if the device doesn't have a assigned ip skip
        ipaddr = ifaddr[2][0]['addr']
        try:
            print(sendrcon("say hi", "brgpsx", ipaddr.strip()))
            foundip = True
            ip = ipaddr
            print(ip)
        except: pass