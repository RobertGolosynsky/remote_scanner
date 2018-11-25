import subprocess
import time
import netifaces
import socket
from functools import wraps


def is_connected():
        try:
                host = socket.gethostbyname("www.google.com")
                s = socket.create_connection((host, 80), 2)
                return True
        except:
                pass
        return False


def turn_off():
	print("Disconecting from internet..")
	subprocess.run(["poff", "rnet"])
	print("Disconected from internet")


def turn_on():
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
				print("ppp0 present, but no internet, retrying in 1 second".format(retry_time))
		if time.time() - start > timeout:
			print("Unable to connect. Timedout {}s".format(timeout))
			break
		time.sleep(retry_time)


def with_internet(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
                turn_on()
                r = f(*args, **kwargs)
                turn_off()
                return r
        return wrapped

