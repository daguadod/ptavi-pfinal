#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import SmallSMILHandler

try:
    fichero = sys.argv[1]
except: 
    sys.exit("Usage: python uaserver.py config")

class config:

    def __init__(self):
        self.list = {}
        self.att = {'account': ['username', 'passwd'],
            'uaserver': ['ip', 'puerto'],
            'rtpaudio': ['puerto'],
            'regproxy': ['ip', 'puerto'],
            'log': ['path'],
            'audio': ['path']}

    def startElement(self, name, attrs):

        if name in self.att:
            for att in self.att[name]:
                self.list[name + "_" + att] = attrs.get(att,"")

    def get_tags(self):
        return self.list
        
"""
class EchoHandler(socketserver.DatagramRequestHandler):

    def handle(self):
        line = self.rfile.read()
        doc = line.decode("utf-8").split(" ")
        METHOD = doc[0]
        if len(doc) < 4 and len(doc) > 0:
            if METHOD == "INVITE":
                print("INVITE RECIVED")
                self.wfile.write(TRYING + RINGING + OK)
            elif METHOD == "BYE":
                print("BYE RECIVED")
                self.wfile.write(OK)
            elif METHOD == "ACK":
                print("ACK RECIVED")
                aEjecutar = "./mp32rtp -i 127.0.0.1 -p 23032 <" + FILE
                os.system(aEjecutar)
            else:
                self.wfile.write(Not_Allowed)
        else:
            self.wfile.write(BAD)
"""
        
if __name__ == "__main__":
    parser = make_parser()
    cHandler = SmallSMILHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(fichero))
    tags = cHandler.get_tags()
    PORT = int(tags["uaserver_puerto"])
    IP = tags["uaserver_ip"]
    serv = socketserver.UDPServer((IP, PORT), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
