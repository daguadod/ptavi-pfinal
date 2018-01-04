#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
import time
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
log_file = tags["log_path"]

#Creamos o usamos el fichero de registro "Log"

def Log(log_file, tiempo, evento):

	fichero = open(log_file, 'a')
	tiempo = time.gmtime(time.time())
	fichero.write(time.strftime('%Y%m%d%H%M%S', tiempo))
	fichero.write(event.replace('\r\n', ' ') + '\r\n')
	fichero.close()

#Creamos el socket.

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	my_socket.connect((Proxy_IP, Proxy_Port))

#Enviamos mensajes en formato SIP según la terminal de comandos.

	if METHOD == "REGISTER":
		LINE = METHOD + " sip:" + My_Name + ":" + My_Port + " SIP/2.0\r\n" \
		    	+ "Expires: " + OPTION + "\r\n\r\n"
		my_socket.send(bytes(LINE, 'utf-8'))
		print ("Sending: " + LINE)
		event = " sent to " + Proxy_IP + ":" + str(Proxy_Port) + ":" + LINE
		tiempo = time.gmtime(time.time())
		Log(log_file, tiempo, event)
		try:
			data = my_socket.recv(1024)
			event = " Received from " + Proxy_IP + ':'
			event += str(Proxy_Port) + ": " + data.decode('utf-8')
			tiempo = time.gmtime(time.time())
			Log(log_file, tiempo, event)
			DECODED = data.decode('utf-8').split()
			if DECODED[1] == "401":
				nonce = DECODED[-1].split('=')[1]
				m = hashlib.sha1()
				m.update(bytes(nonce, 'utf-8'))
				m.update(bytes(contraseña, 'utf-8'))
				response = m.hexdigest()
				LINE += 'Authorization: Digest response=' + response
				print('Enviando: ' + LINE)

				my_socket.send(bytes(LINE, 'utf-8') + b'\r\n\r\n')
				evento = ' Sent to ' + proxy_IP + ':'
				evento += Proxy_Port + ': ' + LINE
				tiempo = time.gmtime(time.time())
				Log(log_file, tiempo, evento)

				data_recv = my_socket.recv(int(proxy_port))

				evento = ' Received from ' + proxy_IP + ':'
				evento += proxy_port + ': ' + data.decode('utf-8')
				tiempo = time.gmtime(time.time())
				Log(log_file, tiempo, evento)

		except ConnectionRefusedError:
		    	sys.exit("Connection Refused")

	elif METHOD == "INVITE":
		SDPHEAD ="\r\n\r\nContent_Type: application/sdp\r\n" + "v=0\r\n" 
		SDPHEAD += "o=" + My_Name + " " + My_IP  \
		   		 + "\r\ns=" + "sesionPrueba\r\nt=0\r\nm=audio " \
		           	 + tags["rtpaudio_puerto"] + " RTP"
		LINE = METHOD + " sip:" + OPTION \
    		+ " SIP/2.0" + SDPHEAD
		my_socket.send(bytes(LINE, 'utf-8'))
		print("Enviando: " + LINE)
		event = ' Sent to ' + Proxy_IP + ':'
		event += str(Proxy_Port) + ': ' + LINE
		tiempo = time.gmtime(time.time())
		Log(log_file, tiempo, event)
		try:
			data = my_socket.recv(1024)
		except ConnectionRefusedError:
			sys.exit("ConnectionRefused")
		DECODED = data.decode('utf-8').split()
		event = ' Received from ' + Proxy_IP + ':'
		event += str(Proxy_Port) + ': ' + data.decode('utf-8')
		tiempo = time.gmtime(time.time())
		Log(log_file, tiempo, event)
		if len(DECODED) != 0:
			if DECODED[1] == "100" and DECODED[4] == "180":
				ACK = "ACK sip:" + OPTION + "SIP/2.0"
				print("Enviando: " + LINE)
				my_socket.send(bytes(ACK, "utf-8"))
				event = ' Received from ' + Proxy_IP + ':'
				event += str(Proxy_Port) + ': ' + data.decode('utf-8')
				tiempo = time.gmtime(time.time())
				Log(log_file, tiempo, event)
			elif DECODED[1] == "404":
			    sys.exit("User not registered, Use REGISTER METHOD")


	elif METHOD == "BYE":
		LINE = METHOD + " sip:" + OPTION + " SIP/2.0"
		print("Enviando: " + LINE)
		my_socket.send(bytes(LINE, "utf-8") + b"\r\n")
		event = ' Sent to ' + Proxy_IP + ':'
		event += str(Proxy_Port) + ': ' + LINE
		tiempo = time.gmtime(time.time())
		Log(log_file, tiempo, event)

	else:
		sys.exit("Method Not Allowed")
