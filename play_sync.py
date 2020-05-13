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
duration2 = 10
ctr=1
pc_time_utc_sec = datetime.datetime.utcnow().timestamp()
times = []
for k in range(duration2):
    print ("click: ", )
    ser_led.write(b'0x00')     # trigger camera
    ser_speaker.write(b'0x00')     # trigger camera
    #beep(1)
    while True:
        now = datetime.datetime.utcnow().timestamp()

        if (now -pc_time_utc_sec)> ctr:
            times.append(now-pc_time_utc_sec)
            #print ("  Done waiting ")
            ctr+=1
            break

np.savetxt('/mnt/53abab64-8e58-435f-ae3f-45613b0ecb71/may_7/time_str.txt',times)
