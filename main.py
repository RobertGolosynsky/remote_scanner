from config import *
from rtlsdr import RTLSDR
from email_sender import EmailSender
from sim800 import Sim800
from main_service import RemoteScannerService
import subprocess
import sys

try:

	receiver = RTLSDR()

	email_sender = EmailSender(gmail_user, gmail_password)

	main_service = RemoteScannerService(receiver, email_sender, recipients, file_path, flat_data_path, img_path)

	modem = Sim800(serial_port)

	modem.set_on_new_message_listener(main_service.process_raw_message_response)

	modem.loop()

except Exception as e:
	print(sys.exc_info())
	subprocess.run(["poff","rnet"])
