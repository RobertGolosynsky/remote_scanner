import serial
import time
from collections import defaultdict
import re
from send_email import scan_and_send
from config import *

class Sim800():

	def __init__(self, port):
		self.listeners = defaultdict(lambda : lambda comm, args: print("Unregistered command",comm,args))
		self.port = port
		
	def setup(self):
		port.write("AT\r\n".encode())
		time.sleep(1)
		port.write("AT+CMGF=1\r\n".encode())

	def send_command(self, comm, callback=lambda resp: None):
		command = comm+"\r\n"
		print("sending command",command)
		port.write(command.encode())
		callback( port.read_until(b"OK").decode("utf-8") )

	def process(self, line):

		if line.startswith("+"):
			print("Command detected", line)
			colon_pos = line.find(":")
			comm = line[1:colon_pos]
			args = line[colon_pos:].split(",")
			args = [arg.strip() for arg in args ]
			self.listeners[comm](comm, args)
		

	def set_listener(self, command, f):
		self.listeners[command]=f

sms_re = re.compile("^[+].+\n((.*\n)+)OK", re.MULTILINE)

def process_raw_message_response(raw):
	print(raw)
	text_match = sms_re.search(raw)
	message = text_match.group(1).strip()
	print("Message:", message)
	min_max_step, interval, time = message.split(",")
	scan_and_send(min_max_step, interval, time, gmail_user, gmail_password)


def new_message_listener(modem, message_id):
	modem.send_command("at+cmgr="+message_id, lambda raw: process_raw_message_response(raw) )




with serial.Serial(port=serial_port, baudrate=115200) as port:
	
	modem = Sim800(port)
	modem.set_listener("CMTI", lambda comm, args :  new_message_listener(modem, args[1]) )
	modem.set_listener("CPIN", lambda comm, args :  modem.setup() )	
	
	modem.setup()
	
	buff = ""
	while True:
		time.sleep(0.01)
		if port.in_waiting>0:
			s = port.read()
			s = s.decode("utf-8") 
			end = s.find("\n")
			if end > -1:
				buff+= s[:end+1]
				print("processing", buff)
				modem.process(buff)
				buff = s[end+1:]	
			else:
				buff+=s

		
		
