import os
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

import subprocess
from numpy import genfromtxt
import matplotlib.pyplot as plt

import sys
from collections import defaultdict
from datetime import datetime


def flatten_and_plot(source_path, data_path, img_path):
	sums = defaultdict(float)
	counts = defaultdict(int)

	def frange(start, stop, step):
	    i = 0
	    f = start
	    while f <= stop:
	        f = start + step*i
	        yield f
	        i += 1

	for line in open(source_path):
	    line = line.strip().split(', ')
	    low = int(line[2])
	    high = int(line[3])
	    step = float(line[4])
	    weight = int(line[5])
	    dbm = [float(d) for d in line[6:]]
	    for f,d in zip(frange(low, high, step), dbm):
	        sums[f] += d*weight
	        counts[f] += weight

	ave = defaultdict(float)
	for f in sums:
	    ave[f] = sums[f] / counts[f]
	with open(data_path, 'w') as file:
		 for f in ave:
		 	file.write('{},{}\n'.format(f, ave[f]))

	data = genfromtxt(data_path, delimiter=',', names=['x','y'])
	
	plt.xlabel('Frequency (MHz)')
	plt.ylabel('Power (dbm)')
	plt.plot([x/1000000 for x in data['x']], data['y'])
	plt.savefig(img_path)


class RTLSDR:
	"""docstring for RTLSDR"""
	def __init__(self):
		a = 1

	def scan(self, min_max_step, interval_s, time, filename):
		# min_max_step = '{}m:{}m:{}k'.format(min_mhz,max_mhz,step_khz);
		args = [
			'rtl_power', 
			'-f',min_max_step, 
			# '-i', str(interval_s), 
			'-1',
			'-g', '50',
			'-e', '{}s'.format(time), 
			filename
			]
		print(args) 
		response = subprocess.run(args)
		response.check_returncode()
		return args


class EmailSender:
	"""docstring for EmailSender"""
	def __init__(self, gmail_user, gmail_password):
		self.gmail_user = gmail_user
		self.gmail_password = gmail_password

	def send(self, recipients, subject, body, attachments):
		COMMASPACE = ', '

		# Create the enclosing (outer) message
		outer = MIMEMultipart()
		outer['Subject'] = subject
		outer['To'] = COMMASPACE.join(recipients)
		outer['From'] = self.gmail_user
		outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
		body = MIMEText(body) # convert the body to a MIME compatible string
		outer.attach(body) # attach it to your main message

		# Add the attachments to the message
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

		# Send the email
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


def scan_and_send(min_max_step,interval,time,user,password):
	file_name = "scan.csv"
	img_path = "scan.png"
	flat_data_path = "scan_flat.csv"

	rtl = RTLSDR()

	# args = rtl.scan(25,1700,200,1,10,file_name)
	args = rtl.scan(min_max_step, interval, time, file_name)	    
	flatten_and_plot(file_name, flat_data_path, img_path)

	email_sender = EmailSender(user, password)

	subject = "Scan taken on {}".format(datetime.now())
	body = "Scan done with command {}".format(" ".join(args[:-1]))
	email_sender.send(["robertgolosynsky@gmail.com"],subject, body, [file_name ,flat_data_path, img_path])

