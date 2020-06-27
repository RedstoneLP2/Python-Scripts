'''
Script Showing Raspberry Pi SoC temp in an ASCII-esque line graph
by RedstoneLP2
'''



#V cputemp in °C * 1000 V
# cat /sys/class/thermal/thermal_zone0/temp


from braillegraph import horizontal_graph
import subprocess
import time
import os
import shutil

refreshRate = 1 # Refresh rate in Hertz (Cycles / Second)
cputemp = []

while True:
	os.system("clear")

	SPOPEN = subprocess.Popen(['cat', '/sys/class/thermal/thermal_zone0/temp'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	currtemp, error = SPOPEN.communicate()
	if error != None:
		print(error)
		continue

	cputemp.append(round(int(currtemp)/1000))


#	print(min(cputemp))
#	print(max(cputemp))

	c, l = shutil.get_terminal_size((80,24))
	
	vistemp = []
	cputemp.reverse()
	
	for count in range(0, c*2):
		
		if count >= len(cputemp):
			break
		
		vistemp.append(cputemp[count] - (min(cputemp) - 20))

	vistemp.reverse()
	cputemp.reverse()
	

	if len(cputemp) >= 512:
		for i in range(0, 200):
			del cputemp[i]

	print(horizontal_graph(vistemp))


	print(cputemp)
	del vistemp
	time.sleep(refreshRate/1)