
from collections import defaultdict
import time


class Sim800():

	buff = ""

	def __init__(self, serial_port):
		self.listeners = defaultdict(lambda : lambda comm, args: print("Unregistered command", comm, args))
		self.port = serial.Serial(port=serial_port, baudrate=115200)

		self.on_new_message_listener = None

		self.set_listener("CMTI", lambda comm, args :  self._message_received_listener(args[1]) )
		self.set_listener("CPIN", lambda comm, args :  self._setup() )	
		
		self._setup()

	
	def loop():	
		while True:
			time.sleep(0.01)
			self._update()
 

	def set_on_new_message_listener(self, listener):
		self.on_new_message_listener = listener


	def _update(self):
		if self.port.in_waiting>0:
			s = self.port.read()
			s = s.decode("utf-8") 
			end = s.find("\n")
			if end > -1:
				self.buff+= s[:end+1]
				print("processing", self.buff)
				self._process(buff)
				self.buff = s[end+1:]	
			else:
				self.buff+=s


	def _send_command(self, comm, callback=lambda resp: None):
		command = comm+"\r\n"
		print("sending command", command)
		self.port.write(command.encode())
		callback( self.port.read_until(b"OK").decode("utf-8") )


	def _set_listener(self, command, f):
		self.listeners[command] = f


	def _setup(self):
		self.port.write("AT\r\n".encode())
		time.sleep(1)
		self.port.write("AT+CMGF=1\r\n".encode())


	def _message_received_listener(self, message_id):
		if not self.on_new_message_listener == None:
			self.send_command("at+cmgr="+message_id, lambda raw: self.on_new_message_listener(raw) )


	def _process(self, line):
		if line.startswith("+"):
			print("Command detected", line)
			colon_pos = line.find(":")
			comm = line[1:colon_pos]
			args = line[colon_pos:].split(",")
			args = [arg.strip() for arg in args ]
			self.listeners[comm](comm, args)
