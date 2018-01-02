#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import SmallSMILHandler

METHOD = {
	"INVITE": answer_code["Trying"] + answer_code["Ringing"} +
	answer_code["OK"],
	"BYE": answer_code["OK"],
	"ACK": answer_code["OK"]
	}
CLIENT_IP = [""]
RTP_PORT = [""]
class EchoHandler(socketserver.DatagramRequestHandler):

    def handle(self):
        line = self.rfile.read().decode("utf-8").split(" ")
        address = self.client_address[0] + ":"+ str(self.client_address[1])
        if not line(0)in METHOD:
		print ("METHOD NOT ALLOWED")
		msg = answer_code["METHOD NOT ALLOWED"]
		self.wfile.write(msg)

	elif line [0] == "INVITE":
		print ("Imprimiendo: " + line[5])
		CLIENT_IP(0,line[5])
		RTP_PORT(0,line[8])
		print ("Puerto RTP:" + str(RTP_PORT[0]))

	elif line[0] == "ACK":
		address = CLIENT_IP[0] + ":" + RTP_PORT[0]
		aEjecutar = "./mp32rtp -i" + CLIENT_IP[0]+ " -p" + RTP_PORT[0]
		print("ACK recibido ejecutando archivo:" , aEjecutar)
		os.system(aEjecutar)
	elif line[0] == "BYE":
		msg = METHOD["BYE"]
		self.wfile.write(msg)
		print("Recibido" + str(line))
		
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
