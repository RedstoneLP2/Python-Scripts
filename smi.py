'''
Script to display gpu usage of amd and nvidia gpu in one graph*
by RedstoneLP2
'''

import sys
import subprocess
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xml.etree.ElementTree as ET
import time
import json



if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

NV = False

def nvidia():

	sp = subprocess.Popen(['nvidia-smi','-x','-q'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	out_str=sp.communicate()[0].decode("utf-8").replace('\n',"").replace('\t', "")

	root = ET.fromstring(out_str)

	#print(root[4][26][0].text)

	return(root)
def amd():

    sp = subprocess.Popen(['rocm-smi', '-u', '-t', '-f', '--json'], stdout= subprocess.PIPE,stderr=subprocess.PIPE)
    
    out_str=sp.communicate()[0].decode("utf-8").replace('\n',"")

    return json.loads(out_str)["card1"]["GPU use (%)"]



fig = plt.figure()
ax = fig.add_subplot(111)

# some X and Y data
x = []
y = []

li, = ax.plot(x, y,'-o')
ax.grid()
ax.set_ylim([0,100])
# draw and show it
fig.canvas.draw()
plt.show(block=False)

i=0

# loop to update the data
#for i in range(10):
while True:
    i+=1
    try:

        if NV:
            root = float(nvidia()[4][26][0].text.split(" ")[0])
        else:
            root = float(amd())



        x.append(i)
        y.append(root)

        if len(y) > 5:
            y.pop(0)
            x.pop(0)

        print(y)

        # set the new data
        li.set_xdata(x)
        li.set_ydata(y)

        ax.relim() 
        ax.autoscale_view(True,True,True) 



        fig.canvas.draw()

        time.sleep(0.01)
        plt.pause(0.0001)
    except KeyboardInterrupt:
        plt.close('all')
        break
    time.sleep(1)