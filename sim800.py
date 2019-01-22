
from collections import defaultdict
import time
import serial

class Sim800():

	buff = ""

	def __init__(self, serial_port):
		self.listeners = defaultdict(lambda : lambda comm, args: print("Unregistered command", comm, args))
		self.serial_port = serial_port
		self.port = serial.Serial(port=serial_port, baudrate=115200)

		self.on_new_message_listener = None
		
		self._set_listener("CMTI", lambda comm, args :  self._message_received_listener(args[1]) )
		self._set_listener("CPIN", lambda comm, args :  self._setup() )	
		self._set_listener("CPMS", lambda comm, args :  self._clear_sms_storage(args) )	
		
		self._setup()

	
	def loop(self):	
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
				self._process(self.buff)
				self.buff = s[end+1:]	
			else:
				self.buff+=s


	def _send_command(self, comm, callback=lambda resp: None):
		command = comm+"\r\n"
		print("Sending command", command)
		self.port.write(command.encode())
		callback( self.port.read_until(b"OK").decode("utf-8") )


	def _set_listener(self, command, f):
		self.listeners[command] = f


	def _setup(self):
		self.port.write("AT\r\n".encode())
		self.port.flush()
		self.port.write("AT+CMGF=1\r\n".encode())
		self.port.flush()
		self.port.write("AT+CPMS=\"ME\",\"ME\",\"ME\"\r\n".encode())
		self.port.flush()

	def _reinit(self):
		self.port.close()
		self.port = serial.Serial(port=self.serial_port, baudrate=115200)

	def _clear_sms_storage(self, args):
		self._send_command("at+cmgd={}, 4".format(args[-2]))
	
	def _message_received_listener(self, message_id):
		if self.on_new_message_listener is not None:
			def wrapper(raw):
				self.on_new_message_listener(raw)
				self._reinit()

			self._send_command("at+cmgr="+message_id, lambda raw :wrapper(raw))


	def _process(self, line):
		if line.startswith("+"):
			print("Command detected", line)
			colon_pos = line.find(":")
			comm = line[1:colon_pos]
			args = line[colon_pos:].split(",")
			args = [arg.strip() for arg in args ]
			self.listeners[comm](comm, args)
