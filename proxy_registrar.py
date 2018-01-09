#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
	fichero = sys.argv[1]
except IndexError:
	sys.exit(Usage: python3 proxy_registar.py config")

METH = {
    "Trying": b"SIP/2.0 100 Trying\r\n\r\n",
    "Ringing": b"SIP/2.0 180 Ringing\r\n\r\n",
    "Ok": b"SIP/2.0 200 OK\r\n\r\n",
    "Bad Request": b"SIP/2.0 400 Bad Request\r\n\r\n",
    "Unauthorized": b"SIP/2.0 401 Unauthorized\r\n",
    "User_Not_Found": b"SIP/2.0 404 User Not Found\r\n\r\n",
    "Method_Not_Allowed": b"SIP/2.0 405 Method Not Allowed\r\n\r\n",
    "Service_Unavailable": b"SIP/2.0 503 Service Unavailable\r\n\r\n"
}

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

parser = make_parser()
cHandler = SmallSMILHandler()
parser.setContentHandler(cHandler)
parser.parse(open(FICHERO))
tags = cHandler.get_tags()

#Declaramos las variables de configuración

server_name = tags["server_name"]
server_ip = tags["server_ip"]
server_port = tags["server_port"]
data_path = tags["database_path"]
pasw_path = tags["database_paswdpath"]
log_file = tags["log_path"]

def Log(log_file, tiempo, evento):
	fichero = open(log_file, 'a')
	tiempo = time.gmtime(time.time())
	fichero.write(time.strftime('%Y%m%d%H%M%S', tiempo))
	fichero.write(event.replace('\r\n', ' ') + '\r\n')
	fichero.close()

class RegisterHandler(socketserver.DatagramRequestHandler):
	"""
	Echo server class
	"""
	client = {}
	nonce = []

	def register2json(self):

		json.dump(self.client, open('registered.json', 'w'))

	def json2registered(self):

		try:
			with open('registered.json') as client_file:
		        self.client = json.load(client_file)
		        self.file_exists = True
		except:
			self.file_exists = False

	def delete(self):

		deleteList = []

		for client in self.client:
			self.expire = int(self.client[client][-1])
			now = time.time()
			if self.expire < now:
		        	deleteList.append(client)
		for cliente in deleteList:
			    print('ELIMINADO ' + cliente)
			    del self.client[cliente]
			self.register2json()

	def handle(self):

		self.json2registered()
		LINE = self.rfile.read().decode('utf-8')
		linea = LINE.split()
		METHOD = linea[0]
		print("El cliente nos manda:" + LINE)

		event = ' Received from ' + self.client_address[0]
		event += ':' + str(self.client_address[1]) + ': '
		event += LINE
		tiempo = time.gmtime(time.time())
		Log(log_file, tiempo, event)

		if METHOD == "REGISTER":

			if "Digest" not in linea:
				self.nonce.append(str(random.randint(0000, 9999)))
		           	answer = METH["Unauthorized"]
		            	answer += 'WWW Authenticate: Digest nonce='
		            	answer += self.nonce[0] + '\r\n\r\n'
		           	self.wfile.write(bytes(answer, 'utf-8'))

				event = ' Sent to ' + self.client_address[0] + ':'
				event += str(self.client_address[1]) + ': '
				event += answer
				tiempo = time.gmtime(time.time())
				Log(log_file, tiempo, event)

			else:

				self.user = linea[1].split(":")[1]
				self.port = linea[1].split(":")[2]
				response = linea[-1].split("=")[1]
				pasw_file = open(pasw_path, 'r')
				pasw_file1 = pasw_file.readlines()
				self.expires = linea[4]
				for LINE in pasw_file1:
					word = linea[1].split("\r\n")
					if linea[0] == self.user:
						password = word[0[.split("=")[1]

#CONTINUAR POR AQUI

if __name__ == "__main__":

	if len(sys.argv)!= 2:
		sys.exit("Usage: python proxy_registrar.py config")

	fichero = sys.argv[1]
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
