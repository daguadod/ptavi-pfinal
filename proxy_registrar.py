#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    fichero = sys.argv[1]
except:
    sys.exit("Usage: python proxy_registrar.py config")

if not os.path.exists(FILE):
    sys.exit("Document does not exist")

TRYING = b"SIP/2.0 100 Trying\r\n\r\n"
RINGING = b"SIP/2.0 180 Ringing\r\n\r\n"
OK = b"SIP/2.0 200 OK\r\n\r\n"
BAD = b"SIP/2.0 400 Bad Request\r\n\r\n"
Unauthorized = b"SIP/2.0 401 Unauthorized\r\n\r\n"
User_Not_Found = b"SIP/2.0 404 User Not Found\r\n\r\n"
Not_Allowed = b"SIP/2.0 405 Method Not Allowed\r\n\r\n"

class SmallSMILHandler(ContentHandler):

    def __init__(self):
        self.list = {}
        self.att = {'server': ['name', 'ip', 'puerto'],
            'database': ['path', 'paswdpath'],
            'log': ['path']}
                    
    def startElement(self, name, attrs):

        if name in self.att:
            for att in self.att[name]:
                self.list[name + "_" + att] = attrs.get(att,"")

    def get_tags(self):
        return self.list

class EchoHandler(socketserver.DatagramRequestHandler):

    def handle(self):
        line = self.rfile.read()
        doc = line.decode("utf-8").split(" ")
        METHOD = doc[0]
        if len(doc) < 4 and len(doc) > 0:
            if METHOD == "INVITE":
                print("INVITE RECIVED")
                self.wfile.write(TRYING + RINGING)
            elif METHOD == "BYE":
                print("BYE RECIVED")
            elif METHOD == "ACK":
                print("ACK RECIVED")
            else:
                self.wfile.write(Not_Allowed)
        else:
            self.wfile.write(BAD)

if __name__ == "__main__":
    parser = make_parser()
    cHandler = SmallSMILHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(fichero))
    tags = cHandler.get_tags()
    PORT = int(tags["server_puerto"])
    IP = tags["server_ip"]
    NAME = tags["server_name"]
    serv = socketserver.UDPServer((IP, PORT), EchoHandler)
    print("Server " + NAME + " listening at port " + str(PORT) )
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
