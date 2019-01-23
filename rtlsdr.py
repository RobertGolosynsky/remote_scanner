
import subprocess


class RTLSDR:
	
	def __init__(self):
		pass

	def scan(self, min_max_step, interval_s, time, filename):
		args = ['rtl_power']
		if interval_s = '0':
  			args.append('-1')
		else:
			args.append('-i')
			args.append(interval_s)
		args+=[
			'-f',min_max_step, 
			'-g', '50',
			'-e', '{}s'.format(time), 
			filename
			] 
		response = subprocess.run(args)
		response.check_returncode()
		return args
