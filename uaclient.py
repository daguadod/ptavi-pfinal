#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

#variables de configuración.
try:
    FICHERO = sys.argv[1]
    METHOD = str.upper(sys.argv[2])
    OPTION = sys.argv[3]
except:
    sys.exit("Usage: python uaclient.py config method option")

#Leemos el fichero xml de configuración.

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

parser = make_parser()
cHandler = SmallSMILHandler()
parser.setContentHandler(cHandler)
parser.parse(open(FICHERO))
tags = cHandler.get_tags()

#Variables para los mensajes.

My_IP = tags["uaserver_ip"]
My_Name = tags["account_username"]
My_Password = tags["account_passwd"]
My_Port = tags["uaserver_puerto"]
Proxy_IP = tags["regproxy_ip"]
Proxy_Port = int(tags["regproxy_puerto"])

#Creamos el socket.

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((Proxy_IP, Proxy_Port))

#Enviamos mensajes en formato SIP según la terminal de comandos.

    if METHOD == "REGISTER":
        LINE = METHOD + " sip:" + My_Name + ":" + My_Port + " SIP/2.0\r\n" \
                + "Expires: " + OPTION + "\r\n\r\n"
        my_socket.send(bytes(LINE, 'utf-8'))
        try:
            data = my_socket.recv(1024)
        except ConnectionRefusedError:
            sys.exit("Connection Refused")
        DECODED = data.decode('utf-8').split()
        if len(DECODE) >= 2:
            if DECODE[2] == "Unauthorized":
                LINE = LINE + " \r\n" + "Authorization: Digest response=" \
                        + My_password
                my_socket.send(bytes(LINE, 'utf-8'))
        
    elif METHOD == "INVITE":
        SDPHEAD ="v=0\r\no=" + My_Name + " " + My_IP  \
                    + "\r\ns=" + "sesionPrueba\r\nt=0\r\nm=audio " \
                    + tags["rtpaudio_puerto"] + " RTP"
        LINE = method + " sip:" + OPTION \
                + " SIP/2.0\r\nContent-Type: application/sdp\r\n\r\n" + SDPHead
        my_socket.send(bytes(LINE, 'utf-8'))
        try:
            data = my_socket.recv(1024)
        except ConnectionRefusedError:
            sys.exit("ConnectionRefused")
        DECODED = data.decode('utf-8').split()
        if len(DECODED) != 0:
            if DECODED[1] == "100" and DECODED[4] == "180":
                ACK = "ACK sip:" + OPTION + "SIP/2.0"
                my_socket.send(bytes(ACK, "utf-8"))
            elif DECODED[1] == "404":
                sys.exit("User not registered")

    elif METHOD == "BYE":
        LINE = METHOD + " sip:" + OPTION + " SIP/2.0"
        my_socket.send(bytes(LINE, "utf-8") + b"\r\n")
        try:
            data = my_socket.recv(1024)
        except ConnectionRefusedError:
            sys.exit("Connection refused")
