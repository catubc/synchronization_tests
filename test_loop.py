import datetime
import os
import time
import numpy as np
# 
#epochs = np.arange(24 * 20) # 24 epochs of 1 hour each ; x 20 days
epochs = np.arange(100) # 24 epochs of 1 hour each ; x 20 days
print (" NEW EXPERIMENT TOTAL # OF EPOCHS: ", epochs.shape[0])

for epoch in epochs:
	#os.system('python /home/cat/code/pyspin_commandline_single_chunk.py')
	os.system('python /home/cat/code/test_pysping_sync.py')

print (" DONE EPOCH: ", epoch, ",  of total: ", epochs)
