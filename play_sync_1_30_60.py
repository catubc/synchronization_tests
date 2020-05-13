import matplotlib

import numpy as np
import datetime
import time
import datetime

import sounddevice as sd

import sys
sys.path.append('/home/cat/Downloads/spinnaker_python-1.27.0.48-Ubuntu18.04-cp37-cp37m-linux_x86_64/Examples/Python3/')

import PySpin

import serial
ser_speaker = serial.Serial(
    port='/dev/ttyUSB3',
    baudrate = 1200,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

ser_led = serial.Serial(
    port='/dev/ttyUSB4',
    baudrate = 20000,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

# launch 
duration2 = 1800
ctr=1
pc_time_utc_sec = datetime.datetime.utcnow().timestamp()
#times_click = np.arange(60,3600,60)
#times_click = np.arange(5,30,55
#times_click = [5,30,55]
times_click = np.arange(1755)
times_idx = 0
times = []
while True:
	now = datetime.datetime.utcnow().timestamp()

	#if (now -pc_time_utc_sec)> ctr:
	if (now -pc_time_utc_sec)> times_click[times_idx]:
		ser_led.write(b'0x00')     # trigger camera
		ser_speaker.write(b'0x00')     # trigger camera
		times.append(now-pc_time_utc_sec)
		#print ("  Done waiting ")
		print ("click time ", times_click[times_idx], " sec")
		#beep(1)
		times_idx+=1            
	
	#if times_idx>=len(times_click):
#		break
	
	if (now -pc_time_utc_sec)> duration2:
		break

print ("Times clicked: ", times)
np.savetxt('/mnt/53abab64-8e58-435f-ae3f-45613b0ecb71/may_12_60sectests/time_str_'+\
			str(round(np.random.rand(),6))+'.txt',times)
