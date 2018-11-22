
import subprocess


class RTLSDR:
	"""docstring for RTLSDR"""
	def __init__(self):
		pass

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
		response = subprocess.run(args)
		response.check_returncode()
		return args
