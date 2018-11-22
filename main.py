from config import *

receiver = RTLSDR()

email_sender = EmailSender(gmail_user, gmail_password)

main_service = RemoteScannerService(receiver, email_sender)

modem = Sim800(serial_port)

modem.set_on_new_message_listener(main_service.process_raw_message_response)

modem.loop()

