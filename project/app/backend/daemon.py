# It might have been cron as well, but Python is easier to run on different computer & more portable

import requests
import sys
import time

server_path = "http://127.0.0.1:5000"

if __name__ == "__main__":
	while True:
		try:
			resp = requests.get(server_path + "/maintenance")
			print(resp)
		except Exception as e:
			print(e)
		time.sleep(1)
