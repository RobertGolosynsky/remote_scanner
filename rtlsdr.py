
import subprocess


class RTLSDR:
	
	def __init__(self):
		pass

	def scan(self, min_max_step, interval_s, time, filename):
		args = [
			'rtl_power', 
			'-f',min_max_step, 
			'-1',
			'-g', '50',
			'-e', '{}s'.format(time), 
			filename
			] 
		response = subprocess.run(args)
		response.check_returncode()
		return args
