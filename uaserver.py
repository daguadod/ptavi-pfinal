#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import threading
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

# Leemos la variable de configuración.

try:
    FICHERO = sys.argv[1]
except IndexError:
    sys.exit("Usage: python3 uaserver.py config")

# Obtenemos las variables de configuración del fichero anterior.


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
                self.list[name + "_" + att] = attrs.get(att, "")

    def get_tags(self):
        return self.list

parser = make_parser()
cHandler = SmallSMILHandler()
parser.setContentHandler(cHandler)
parser.parse(open(FICHERO))
tags = cHandler.get_tags()

# Creamos/ utilizamos el fichero log de registro de actividad.


def log(log_file, event):

    fichero = open(log_file, "a")
    tiempo = time.gmtime(time.time())
    fichero.write(time.strftime("%Y%m%d%H%M%S", tiempo))
    fichero.write(event.replace("\r\n", " ") + "\r\n")
    fichero.close()

# Declaramos las diferentes respuestas a los mensajes recibidos.


METHOD = {
    "INVITE": "SIP/2.0 100 Trying\r\n\r\n" + "SIP/2.0 180 Ring\r\n\r\n" +
    "SIP/2.0 200 OK\r\n\r\n",
    "BYE": "SIP/2.0 200 OK\r\n\r\n",
    "Not_Allowed": "SIP/2.0 405 Method Not Allowed\r\n\r\n",
    "Bad_Request": "SIP/2.0 400 Bad Request"
    }

# Declaramos las variables de configuración.

My_IP = tags["uaserver_ip"]
if My_IP == "":
    My_IP = "127.0.0.1"
My_Name = tags["account_username"]
My_Password = tags["account_passwd"]
My_Port = tags["uaserver_puerto"]
Proxy_IP = tags["regproxy_ip"]
Proxy_Port = int(tags["regproxy_puerto"])
log_file = tags["log_path"]
RTP_PORT = tags["rtpaudio_puerto"]
audio_file = tags["audio_path"]


event = " Starting uaserver..."
log(log_file, event)

# Procedimiento para interacuar con los mensajes recibidos.


class EchoHandler(socketserver.DatagramRequestHandler):

    rtp_list = []

    def handle(self):

        linea = self.rfile.read().decode('utf-8')
        LINE = linea.split()
        print("Received :" + linea)
        address = self.client_address[0] + ":" + str(self.client_address[1])
        event = " Received from" + Proxy_IP + ":" + str(Proxy_Port) + ": "
        event += linea
        log(log_file, event)
        if LINE[0] == "INVITE":
            v = "v=0\r\n"
            o = "o=" + My_Name + " " + My_IP
            o += " \r\n"
            s = "s= misesion\r\n"
            t = "t=0" + "\r\n"
            m = "m=audio " + RTP_PORT + " RTP\r\n"
            sdp = v + o + s + t + m
            ANSW = METHOD["INVITE"] + sdp
            self.wfile.write(bytes(ANSW, 'utf-8'))
            event = ' Sent to ' + Proxy_IP + ':'
            event += str(Proxy_Port) + ': ' + ANSW
            log(log_file, event)

            self.rtp_user = LINE[6].split("=")[1]
            self.rtp_list.append(self.rtp_user)
            self.rtp_ip = LINE[7]
            self.rtp_list.append(self.rtp_ip)
            self.rtpaudio_port = LINE[11]
            self.rtp_list.append(self.rtpaudio_port)

        elif LINE[0] == "ACK":
            aEjecutar = "./mp32rtp -i " + self.rtp_list[1] + " -p "
            aEjecutar += self.rtp_list[2]
            aEjecutar += " < " + audio_file
            print("ACK received, running file:", aEjecutar)
            os.system(aEjecutar)
            event = ' Sending to ' + self.rtp_list[1] + ":"
            event += self.rtp_list[2] + ": " + audio_file
            log(log_file, event)

        elif LINE[0] == "BYE":

            ANSW = METHOD["BYE"]
            self.wfile.write(bytes(ANSW, 'utf-8'))
            print("Received" + str(ANSW))

            event = ' Sent to ' + Proxy_IP + ':'
            event += str(Proxy_Port) + ': ' + ANSW
            log(log_file, event)

        elif LINE.split()[1] == "200":
            event = " Received from" + Proxy_IP + ":" + str(Proxy_Port) + ": "
            event += linea
            log(log_file, event)

        elif not LINE[0] in METHOD:
            ANSW = METHOD["Not_Allowed"]
            self.wfile.write(bytes(ANSW, 'utf-8'))
            event = " Sent to " + Proxy_IP + ":"
            event += str(Proxy_Port) + ': ' + ANSW
            log(log_file, event)

        else:
            ANSW = METHOD["Bad_Request"]
            self.wfile.write(bytes(ANSW, 'utf-8'))
            event = " Sent to " + proxy_IP + ":"
            event += Proxy_Port + ': ' + ANSW
            log(log_file, event)

# Creamos el socket servidor.

if __name__ == "__main__":
    try:
        serv = socketserver.UDPServer((My_IP, int(My_Port)), EchoHandler)
        print("Listening...")
        serv.serve_forever()
    except KeyboardInterrupt:
        event = " Finishing uaserver."
        log(log_file, event)
        sys.exit("\r\nFinished uaserver")
