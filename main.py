import config
from rtlsdr import RTLSDR
from email_sender import EmailSender
from sim800 import Sim800
from main_service import RemoteScannerService
import subprocess
import sys
import ppp_service

def main():
	receiver = RTLSDR()

	email_sender = EmailSender(config.mail_user, config.mail_password)

	main_service = RemoteScannerService(
		receiver, email_sender,
		config.recipients,
		config.file_path, config.flat_data_path, config.img_path
		)

	modem = Sim800(config.serial_port)

	modem.set_on_new_message_listener(main_service.process_raw_message_response)

	modem.loop()
try:
	main()
except Exception as e:
	print(sys.exc_info())
	ppp_service.turn_off()
	raise
