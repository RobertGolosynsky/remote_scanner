import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import os
import sys
from functools import wraps
import subprocess
import netifaces 
import time
import socket

 
def is_connected():
  try:
    host = socket.gethostbyname("www.google.com")
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False


def with_internet(f):
	@wraps(f)
	def wrapped(*args, **kwargs):
		print("Connecting to internet...")
		subprocess.run(["pon", "rnet"])
		start = time.time()
		timeout = 20
		retry_time = 1
		while True:
			if "ppp0" in netifaces.interfaces():
				if is_connected():
					print("Connected to internet!")
					break
				else:
					print("ppp0 present, but no internet, reptying in 1 second".format(retry_time))
			if time.time() - start > timeout:
				print("Unable to connect. Timedout {}s".format(timeout))
				break
			time.sleep(retry_time)				
		r = f(*args, **kwargs)
		print("Disconecting from internet..")
		subprocess.run(["poff", "rnet"])
		print("Disconected from internet")
		return r
	return wrapped

class EmailSender:
	
	"""docstring for EmailSender"""
	def __init__(self, gmail_user, gmail_password):
		self.gmail_user = gmail_user
		self.gmail_password = gmail_password
	
					
	@with_internet
	def send(self, recipients, subject, body, attachments):
		COMMASPACE = ', '

		outer = MIMEMultipart()
		outer['Subject'] = subject
		outer['To'] = COMMASPACE.join(recipients)
		outer['From'] = self.gmail_user
		outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
		body = MIMEText(body) 
		outer.attach(body) 

		for file in attachments:
			try:
				with open(file, 'rb') as fp:
					msg = MIMEBase('application', "octet-stream")
					msg.set_payload(fp.read())
				encoders.encode_base64(msg)
				msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
				outer.attach(msg)
			except Exception as e:
				print("Unable to open one of the attachments. Error: ", e)
				raise

		composed = outer.as_string()

		try:
			with smtplib.SMTP('smtp.gmail.com', 587) as s:
				s.ehlo()
				s.starttls()
				s.ehlo()
				s.login(self.gmail_user, self.gmail_password)
				s.sendmail(self.gmail_user, recipients, composed)
				s.close()
			print("Email sent!")
		except Exception as e:
			print("Unable to send the email. Error: ", e)
			raise
