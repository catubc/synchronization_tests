
import numpy as np
import datetime
import cv2
import os
import sounddevice as sd
import time

import subprocess

import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append('/home/cat/Downloads/spinnaker_python-1.27.0.48-Ubuntu18.04-cp37-cp37m-linux_x86_64/Examples/Python3/')

import PySpin

# ************* TTL AND LED TRIGGERS FUCNTIONS **************
def ttl_audio_and_led(duration):
	print ("START BEEPS ***************")
	import serial
	ser_speaker = serial.Serial(
		port='/dev/ttyUSB3',
		baudrate = 9600,
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
	#duration2 = 3600
	ctr=1
	pc_time_utc_sec = datetime.datetime.utcnow().timestamp()
	times = []
	for k in range(duration2):
		print ("click ... led ... ", )
		ser_led.write(b'0x00')     # trigger camera
		ser_speaker.write(b'0x00')     # trigger camera

		# wait until 1 sec up and save time;
		while True:
			now = datetime.datetime.utcnow().timestamp()

			if (now -pc_time_utc_sec)> ctr:
				times.append(now-pc_time_utc_sec)
				#print ("  Done waiting ")
				ctr+=1
				break

	np.savetxt('/mnt/53abab64-8e58-435f-ae3f-45613b0ecb71/sync_test/time_str.txt',times)


# ************* INITIALIZE CAMERAS **************
def init_camera(capture_FPS):
	# check to make sure previous cam intialization was ended;
	# I think this is redundant
	try: 
		cam.EndAcquisition()
	except:
		pass

	print ("")
	print ("")
	print ("")

	print ("re init camera")

	# Retrieve list of cameras from the system
	cam_list = system.GetCameras()
	num_cameras = cam_list.GetSize()
	cam = cam_list[0]

	# Retrieve TL device nodemap and print device information
	nodemap_tldevice = cam.GetTLDeviceNodeMap()

	# Initialize camera
	cam.Init()

	# Retrieve GenICam nodemap
	nodemap = cam.GetNodeMap()

	# Acquire images
	#acquire_images(cam, nodemap, nodemap_tldevice)

	node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))

	node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')

	acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

	# set the frame rate manually
	cam.AcquisitionFrameRateEnable.SetValue(True)
	cam.AcquisitionFrameRate.SetValue(capture_FPS)

	# check frame rate is correct
	node_acquisition_framerate = PySpin.CFloatPtr(nodemap.GetNode("AcquisitionFrameRate"))
	framerate_to_set = node_acquisition_framerate.GetValue()
	print ("Frame rate to be set to %dFPS" % framerate_to_set)

	# Set integer value from entry node as new value of enumeration node
	node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

	return cam
	
# ************* INITIALIZE MICROPHONE **************
def init_audio(fs):
	# initialize microphone
	sd.default.device = 'UltraMic384K'
	print (sd.query_devices())

	# setup audio recording parameters
	# duration = 10  # seconds
	#fs = 384000
	sd.default.samplerate = fs
	sd.default.channels = 1

	return sd

# ***********  MAKE REQUIRED DIRECTORES *************
def make_directories(root_dir):
	try:
		os.mkdir(root_dir)
	except:
		pass
	try:
		os.mkdir(root_dir+'/audio/')
	except:
		pass

	try:
		os.mkdir(root_dir+'/video/')
	except:
		pass

	try:
		os.mkdir(root_dir+'/times/')
	except:
		pass

# *******************************************************
# *******************************************************
# *******************************************************

# Retrieve singleton reference to system object
system = PySpin.System.GetInstance()

# Get current library version
version = system.GetLibraryVersion()
print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))


# ************* INITIALIZE USB **************
# dont' recall need the reason for this
sudoPassword = 'sanes2020'
command = 'sh -c "echo 4000 > /sys/module/usbcore/parameters/usbfs_memory_mb"'
p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))

# set default saving directory
root_dir = '/mnt/53abab64-8e58-435f-ae3f-45613b0ecb71/may_8_3600tests/'
make_directories(root_dir)

# framerate of camera
capture_FPS = 25
fs = 384000

# set opencv recorder parameters;
# currently using this rsolution; 
height, width, layers = [1280,1024,3]
size= (height, width)

# number of seconds per epoch
duration = 3600 
print (" New acquisition: Grabbing frames: ", capture_FPS*duration)

# number of hours of recording
#epochs = np.arange(24*20) #24 - 1 hour epochs x 20 days
#print (" # of epocs: ", epochs.shape[0], " , duration each: ", duration, 
#	   " , seconds", ", TOTAL TIME: ", epochs.shape[0]*duration, " sec")
# start acquisition loop
times = []

print (" RUNNING EPOCH DURATION: ", duration, " SEC" )

# start video acquisition and grab individual video files
cam = init_camera(capture_FPS)

# grab pc time stamp at acquisition start; Approximate start of video
pc_time_utc_sec = datetime.datetime.utcnow().timestamp()
time_str = datetime.datetime.fromtimestamp(pc_time_utc_sec).strftime("%Y-%-m-%-d_%I:%M:%S:%f")

# start a new video file
cv2_file = root_dir+'/video/'+str(time_str)+'.avi'
out = cv2.VideoWriter(cv2_file, cv2.VideoWriter_fourcc(*'DIVX'), capture_FPS, size)
	
# time stamp file
time_stamp_file = root_dir+'/times/'+str(time_str)+'.txt'
times = []

# start a new audio file
audio_file = root_dir+'/audio/'+str(time_str)+'.npy'

# ********* START LED/BEEPS ASYNCRHONOSOULY *******
#parmap.map_async(ttl_audio_and_led, [duration])
subprocess.call("python play_sync_1_30_60.py &", shell=True)

# ********* START AUDIO ***********
# start audio acquisition after camera to get closer to realtime alignment
sd = init_audio(fs)
audio_rec = sd.rec(int(duration * fs))

# ********* START VIDEO
# begin camera acquisition
cam.BeginAcquisition()
k=0
while True:

	image_result = cam.GetNextImage()
	time = datetime.datetime.fromtimestamp(image_result.GetTimeStamp()/1e9).timestamp()
	times.append(time)
	
	#cam_time_utc_sec = datetime.datetime.utcfromtimestamp(image_result.GetTimeStamp()/1e9).timestamp()

	if k%100==0:
	   print ("frame: ", k, " time: ", time)

	# convert image to bgr for saving
	images_avi = image_result.Convert(PySpin.PixelFormat_BGR8)

	# add image to opencv avi file
	out.write(images_avi.GetData().reshape((1024, 1280, 3)))

	# release iamge
	image_result.Release()
	
	k+=1
	
	now = datetime.datetime.utcnow().timestamp()
	
	if (now -pc_time_utc_sec)> duration:
		print ("  Done recording ", duration, " seconds... closing ")
		break
	
# close the video recording
out.release()

# save audio
np.save(audio_file,audio_rec)

# save time stamp file
np.savetxt(time_stamp_file, times, fmt='%f')

# close audio rec
sd.stop()

# close the camera
cam.EndAcquisition()

# deiniatlize camera
cam.DeInit()

# stop an delete camera
try:
	del cam
	del audio_rec 
	del out
except:
	print (" didn't delete cam")
