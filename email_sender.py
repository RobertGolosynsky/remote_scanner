from ppp_service import with_internet
import config
import sys


import base64
import sendgrid
import os
from sendgrid.helpers.mail import Email, Content, Mail, Attachment
import urllib.request as urllib



class EmailSender:
	
	
	def __init__(self, api_key):
		self.api_key = api_key
	
	def _decide_content_type(self, file_path):
		filename = os.path.basename(file_path)
		if filename.endswith(".csv"):
			return "text/csv"
		if filename.endswith(".eps"):
			return "application/postscript"
		return "application/octet-stream"

					
	@with_internet
	def send(self, recipient, subject, body, attachments):
		
		sg = sendgrid.SendGridAPIClient(apikey=self.api_key)
		from_email = Email("remotescanner1337@gmail.com")
		to_email = Email(recipient)
		content = Content("text/html", body)

		mail = Mail(from_email, subject, to_email, content)

		for file_path in attachments:
			try:
				with open(file_path,'rb') as f:
				    data = f.read()

				encoded = base64.b64encode(data).decode()

				attachment = Attachment()
				attachment.content = encoded
				attachment.type = self._decide_content_type(file_path)
				attachment.filename = os.path.basename(file_path)
				attachment.disposition = "attachment"
				mail.add_attachment(attachment)

			except Exception as e:
				print("Unable to open one of the attachments. Error: ", e)
				raise

		try:
		    response = sg.client.mail.send.post(request_body=mail.get())
		except urllib.HTTPError as e:
		    print(e.read())
		    raise
		print("Email sent!")
