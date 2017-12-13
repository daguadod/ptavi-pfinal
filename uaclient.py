#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    FICHERO = sys.argv[1]
    METHOD = sys.argv[2]
    OPTION = sys.argv[3]
except:
    sys.exit("Usage: python uaclient.py config method option")

class SmallSMILHandler(ContentHandler):

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

if __name__ == "__main__":
    parser = make_parser()
    cHandler = SmallSMILHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(fichero))
    tags = cHandler.get_tags()
    PORT = int(tags["uaserver_puerto"])
    IP = tags["uaserver_ip"]

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP, PORT))
        my_socket.send(bytes(LINE, "utf-8") + b"\r\n")
        data = my_socket.recv(1024)
