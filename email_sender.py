import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import os
import sys


class EmailSender:
	
	"""docstring for EmailSender"""
	def __init__(self, gmail_user, gmail_password):
		self.gmail_user = gmail_user
		self.gmail_password = gmail_password

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
		    except:
		        print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
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
		except:
		    print("Unable to send the email. Error: ", sys.exc_info()[0])
		    raise
