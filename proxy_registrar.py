#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import random
import hashlib
import socket
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

# Leemos la variable de configuración.

try:
    fichero = sys.argv[1]
except IndexError:
    sys.exit("Usage: python3 proxy_registar.py config")

# Creamos las respuestas para los distintos mensajes que nos llegan.

METH = {
    "Trying": b"SIP/2.0 100 Trying\r\n\r\n",
    "Ringing": b"SIP/2.0 180 Ringing\r\n\r\n",
    "Ok": b"SIP/2.0 200 OK\r\n\r\n",
    "Bad Request": b"SIP/2.0 400 Bad Request\r\n\r\n",
    "Unauthorized": "SIP/2.0 401 Unauthorized\r\n\r\n",
    "User_Not_Found": b"SIP/2.0 404 User Not Found\r\n\r\n",
    "Method_Not_Allowed": b"SIP/2.0 405 Method Not Allowed\r\n\r\n"
    }

# Leemos el fichero de configuración.


class SmallSMILHandler(ContentHandler):

    def __init__(self):
        self.list = {}
        self.att = {"server": ["name", "ip", "puerto"],
                    "database": ["path", "passwdpath"],
                    "log": ["path"]}

    def startElement(self, name, attrs):

        if name in self.att:
            for att in self.att[name]:
                self.list[name + "_" + att] = attrs.get(att, "")

    def get_tags(self):
        return self.list

parser = make_parser()
cHandler = SmallSMILHandler()
parser.setContentHandler(cHandler)
parser.parse(open(fichero))
tags = cHandler.get_tags()

# Declaramos las variables de configuración y de los mensajes.

server_name = tags["server_name"]
server_ip = tags["server_ip"]
server_port = tags["server_puerto"]
data_path = tags["database_path"]
pasw_path = tags["database_passwdpath"]
log_file = tags["log_path"]

# Opcion que configura el fichero log.


def log(log_file, event):
    fichero = open(log_file, "a")
    tiempo = time.gmtime(time.time())
    fichero.write(time.strftime("%Y%m%d%H%M%S", tiempo))
    event = event.replace("\r\n", " ")
    fichero.write(event + "\r\n")
    fichero.close()

# Creamos la clase para registrar a los distintos usuarios.


class RegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    client = {}
    nonce = []

    def register2json(self):

        json.dump(self.client, open("registered.json", "w"))

    def json2registered(self):

        try:
            with open("registered.json") as client_file:
                self.client = json.load(client_file)
                self.file_exists = True
        except:
            self.file_exists = False

# Con el procedimiento delete borramos los usuarios caducados.

    def delete(self):

        delete_list = []

        for client in self.client:
            self.expire = int(self.client[client][-1])
            now = time.time()
            if self.expire < now:
                delete_list.append(client)
        for cliente in delete_list:
            print("DELETING " + cliente)
            del self.client[cliente]
        self.register2json()

# Procedimiento para interactuar con los mensajes que recibimos.

    def handle(self):

        self.json2registered()
        self.delete()
        LINE = self.rfile.read().decode('utf-8')
        print("CLient sends:" + LINE)
        linea = LINE.split()
        METHOD = linea[0]

        event = " Received from " + self.client_address[0]
        event += ":" + str(self.client_address[1]) + ": "
        event += LINE
        log(log_file, event)

        if METHOD == "REGISTER":

            if "Digest" not in linea:
                self.nonce.append(str(random.randint(0000, 9999)))
                answer = METH["Unauthorized"]
                answer += "WWW-Authenticate: Digest nonce="
                answer += self.nonce[0] + "\r\n\r\n"
                self.wfile.write(bytes(answer, 'utf-8'))

                event = " Sent to " + self.client_address[0] + ":"
                event += str(self.client_address[1]) + ": "
                event += answer
                log(log_file, event)

            else:

                self.user = LINE.split()[1].split(":")[1]
                self.port = LINE.split()[1].split(":")[2]
                response = LINE.split()[-1].split("=")[1]
                pasw_file = open(pasw_path, "r")
                pasw_file1 = pasw_file.readlines()
                self.expire = LINE.split()[4]
                for LINE in pasw_file1:
                    linea = LINE.split()
                    word = linea[2].split("\r\n")
                    if linea[0] == self.user:
                        password = word[0].split("=")[1]
                        m = hashlib.sha1()
                        m.update(bytes(self.nonce[0], 'utf-8'))
                        m.update(bytes(password, 'utf-8'))
                        response_comparation = m.hexdigest()
                        if response_comparation == response:
                            self.json2registered()
                            self.now = time.time()
                            self.expire_time = float(self.expire) + \
                                float(self.now)
                            self.cliente_lista = []
                            self.cliente_lista.append(self.client_address[0])
                            self.cliente_lista.append(self.port)
                            self.cliente_lista.append(self.now)
                            self.cliente_lista.append(self.expire_time)
                            self.client[self.user] = self.cliente_lista
                            self.cliente_lista = []
                            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

                            event = " Sent to " + self.client_address[0]
                            event += ":" + str(self.port) + ": "
                            event += "SIP/2.0 200 OK\r\n\r\n"
                            log(log_file, event)

                self.register2json()

        elif METHOD == "INVITE":

            self.json2registered()
            user1 = linea[6].split("=")[1]
            user = LINE.split()[1].split(":")[1]

            if user and user1 in self.client.keys():

                self.json2registered()
                IP_server = self.client[user][0]
                PORT_server = self.client[user][1]
                my_socket = socket.socket(socket.AF_INET,
                                          socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((IP_server, int(PORT_server)))
                my_socket.send(bytes(LINE, 'utf-8'))

                event = " Sent to " + IP_server + ":"
                event += PORT_server + ": " + LINE
                log(log_file, event)

                try:
                    data = my_socket.recv(int(server_port))
                    data_recived = data.decode('utf-8')

                    event = " Received from " + IP_server
                    event += ":" + PORT_server + ":" + data_recived
                    log(log_file, event)

                    print("Received --  ", data_recived)
                    self.wfile.write(bytes(data_recived, 'utf-8'))
                except ConnectionRefusedError:
                    self.wfile.write(bytes("Connection Refused", 'utf-8'))
                    print("Connection Refused")
                    event = " Connection Refused " + IP_server + ":"
                    event += PORT_server
                    log(log_file, event)

            else:

                self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")

                event = " Sent to " + self.client_address[0] + ":"
                event += str(self.client_address[1]) + ":" + LINE
                log(log_file, event)

        elif METHOD == "ACK":

            self.json2registered()
            user = LINE.split()[1].split(":")[1]
            IP_server = self.client[user][0]
            PORT_server = self.client[user][1]
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((IP_server, int(PORT_server)))
            my_socket.send(bytes(LINE, 'utf-8'))

            event = " Sent to " + IP_server + ":" + PORT_server
            event += PORT_server + ":" + LINE
            log(log_file, event)

            data = my_socket.recv(int(server_port))
            data_recived = data.decode('utf-8')

            event = " received from " + IP_server + ": "
            event += PORT_server + ": " + data_recived
            log(log_file, event)

            print("Recibido -- ", data_recived)
            self.wfile.write(bytes(data_recived, 'utf-8') + b"\r\n")

            event = " Sent to " + self.client_address[0] + ":"
            event += str(self.client_address[1]) + ": " + LINE
            log(log_file, event)

        elif METHOD == "BYE":

            self.json2registered()
            user = LINE.split()[1].split(":")[1]
            IP_server = self.client[user][0]
            PORT_server = self.client[user][1]
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((IP_server, int(PORT_server)))
            my_socket.send(bytes(LINE, 'utf-8'))

            event = " Sent to " + IP_server + ": " + PORT_server
            event += ": " + LINE
            log(log_file, event)

            data = my_socket.recv(int(server_port))
            data_recived = data.decode('utf-8')

            event = " Received from " + IP_server + ":"
            event += PORT_server + ": " + data_recived
            log(log_file, event)

            print(" Received -- ", data_recived)
            self.wfile.write(bytes(data_recived, 'utf-8'))

            event = " Sent to " + self.client_address[0] + ":"
            event += str(self.client_address[1]) + ": " + data_recived
            log(log_file, event)

        elif METHOD != 'REGISTER' or 'INVITE' or 'ACK' or 'BYE':

            answer = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
            self.wfile.write(bytes(answer, 'utf-8'))

            event = " Sent to " + self.client_address[0] + ":"
            event += str(self.client_address[1]) + ":" + answer
            log(log_file, event)

        else:

            answer = "SIP/2.0 400 Bad Request\r\n\r\n"
            self.wfile.write(bytes(answer, 'utf-8'))

            event = " Sent to" + self.client_address[0] + ":"
            event += str(self.client_address[1]) + ": " + answer
            log(log_file, event)

# El procedimiento principal con el que creamos le socket server.

if __name__ == "__main__":

    event = " Starting..."
    log(log_file, event)
    try:
        serv = socketserver.UDPServer((server_ip, int(server_port)),
                                      RegisterHandler)
        print(server_name + "listening at port" + server_port + "...")
        serv.serve_forever()
    except KeyboardInterrupt:
        event = " Finishing proxy_registrar."
        log(log_file, event)
    sys.exit("\r\nFinished" + server_name)
