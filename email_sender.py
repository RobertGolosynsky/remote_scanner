import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import os
import sys
from ppp_service import with_internet
import time
import config


class EmailSender:
	
	
	def __init__(self, mail_user, mail_password):
		self.mail_user = mail_user
		self.mail_password = mail_password
	
					
	@with_internet
	def send(self, recipients, subject, body, attachments):
		COMMASPACE = ', '

		outer = MIMEMultipart()
		outer['Subject'] = subject
		outer['To'] = COMMASPACE.join(recipients)
		outer['From'] = self.mail_user
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
			with smtplib.SMTP(config.smtp_server, config.smtp_port) as s:
				s.ehlo()
				s.starttls()
				s.ehlo()
				s.login(self.mail_user, self.mail_password)
				s.sendmail(self.mail_user, recipients, composed)
				s.close()
			print("Email sent!")
		except Exception as e:
			print("Unable to send the email. Error: ", e)
			raise
