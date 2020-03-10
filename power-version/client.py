from Crypto import Random
from Crypto.Cipher import AES

import base64
import socket
import sys

# Simulation Libraries
import random
import time

ACTIONS = ['muscle', 'weightlifting', 'shoutout', 'dumbbells', 'tornado', 'facewipe', 'pacman', 'shootingstar']
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']

class client:

	def __init__(self, ip_addr, port_num):

		# Create TCP/IP socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect to server
		server_address = (ip_addr, port_num)
		print('Initiating connection to %s port %s' % server_address, file=sys.stderr)
		self.sock.connect(server_address)
		print('Connected to %s port %s' % server_address, file=sys.stderr)
			
		# Obtain secret key from local key file 
		with open('key') as key:
			self.secret_key = key.read()
			key.closed

	def run(self):

		action = ''
		cumulativepower_list = []
		in_text = ''

		# Send data until logout action is recieved
		while in_text != 'out':

			print("Press enter to 'dance'. Enter out to exit")
			in_text = sys.stdin.readline().strip()

			# 1. Get action, current and voltage from prediction.py (Simulated)
			position = random.randrange(0, len(POSITIONS))
			action = random.randrange(0, len(ACTIONS))
			current = random.uniform(0, 3)
			voltage = random.uniform(0, 5)
			time_sync = random.uniform(0.5, 5.0)

			if in_text == 'out':
				actual_action = 'logout'
			else:
				actual_action = ACTIONS[action]

			#1a. Calculates average power since first reading
			power = voltage * current
			voltage_str = str(round(voltage, 2))
			current_str = str(round(current, 2))
			power_str = str(round(power,2))
			cumulativepower_list.append(power)
			cumulativepower_list_avg = float(sum(cumulativepower_list) / len(cumulativepower_list))
			
			#1b. Assemble message
			msg = b'#' + b'|'.join([POSITIONS[position].encode(), actual_action.encode(), voltage_str.encode(), current_str.encode(), power_str.encode(), str(round(cumulativepower_list_avg, 2)).encode(), str(round(time_sync, 2)).encode()]) + b'|'
			#msg = b'#' + b'|'.join([POSITIONS[position].encode(), actual_action1.encode(), actual_action2.encode(), actual_action3.encode(), voltage_str.encode(), current_str.encode(), power_str.encode(), str(round(cumulativepower_list_avg, 2)).encode()]) + b'|'
			print('Unencrypted msg[{0}]: {1}'.format(len(msg), msg))

			#2. Encrypt readings
			#2a. Apply padding
			length = 16 - (len(msg) % 16)
			msg += bytes([length])*length
			#print('Padded msg[{0}]: {1}'.format(len(msg), msg))
			
			#2b. Apply AES-CBC encryption
			iv = Random.new().read(AES.block_size)
			#print('IV Length: {0}'.format(len(iv))) # 16 - ok
			cipher = AES.new(self.secret_key.encode(), AES.MODE_CBC, iv)
			#print('Cipher[{0}]: {1}'.format(len(cipher.encrypt(msg)), cipher.encrypt(msg))) # 48 - ok
			
			encodedMsg = base64.b64encode((iv + cipher.encrypt(msg)))
			#print('Encrypted msg[{0}]: {1}'.format(len(encodedMsg), encodedMsg))

			#3. Send data packet over
			print('Sending msg')
			self.sock.sendall(encodedMsg)

			#4. Receive data 
			new_positions = self.sock.recv(1024).decode("utf8")
			print('New Positions Received: {0}'.format(new_positions))
		
		#4. All done, logout.
		self.sock.close()
		sys.exit()


def main():

	if len(sys.argv) != 3:
		print('Invalid number of arguments')
		print('python client.py [IP address] [Port]')
		sys.exit()

	ip_addr = sys.argv[1]
	port_num = int(sys.argv[2])

	my_client = client(ip_addr, port_num)
	my_client.run()

if __name__ == '__main__':
    main()
