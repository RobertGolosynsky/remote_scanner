import serial

from collections import defaultdict
import re
from numpy import genfromtxt  
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from datetime import datetime


class RemoteScannerService():
	
	sms_re = re.compile("^[+].+\n((.*\n)+)OK", re.MULTILINE)

	def __init__(self, sdr, email_sender, recipient, file_name , flat_data_path, img_path):
		self.sdr = sdr
		self.email_sender = email_sender
		self.recipient = recipient
		self.file_name = file_name
		self.flat_data_path = flat_data_path
		self.img_path = img_path


	def process_raw_message_response(self, raw):
		print(raw)
		text_match = self.sms_re.search(raw)
		message = text_match.group(1).strip()
		print("Message:", message)
		min_max_step, interval, time = message.split(",")
		self._scan_and_send(min_max_step, interval, time)


	def _scan_and_send(self, min_max_step, interval, time):

		args = self.sdr.scan(min_max_step, interval, time, self.file_name)
			    
		self._flatten_readings(self.file_name, self.flat_data_path)
		self._plot(self.flat_data_path, self.img_path)

		subject = "Scan taken on {}".format(datetime.now())
		body = "Scan done with command {}".format(" ".join(args[:-1]))
		self.email_sender.send(self.recipient, subject, body, [self.file_name , self.flat_data_path, self.img_path])


	def _flatten_readings(self, source_path, data_path):
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
			for f in sorted(ave):
			 	file.write('{},{}\n'.format(f, ave[f]))

		

	def _plot(self, data_path, img_path):
		data = genfromtxt(data_path, delimiter=',', names=['x','y'])
		plt.figure(figsize=(40, 10))
		plt.xlabel('Frequency (MHz)')
		plt.ylabel('Power (dbm)')
		plt.plot([x/1000000 for x in data['x']], data['y'])
		plt.savefig(img_path, format='eps', dpi=900)


