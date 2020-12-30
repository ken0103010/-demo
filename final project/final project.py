import matplotlib.pyplot as plt
import numpy as np
import time
import time, random
import math
import serial
from collections import deque
from scipy import signal

#Display loading 
class PlotData:
    def __init__(self, max_entries=30):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.check = 0
        self.peak = 0
        self.time = 0
        self.time_next = 0
        self.heartrate = 0
        self.heartrate_ar = []
        
    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        
    def heart_rate(self, y):
        #heart rate cal
        if(self.check == 0):
            if(self.peak < y):
                self.peak = y
                self.time = time.time()

        if(self.check == 0 and (time.time()-self.time) >= 0.3):
                self.check = 1
                self.peak = 0

        if(self.peak < y and self.check == 1):
            self.peak = y
            self.time_next = time.time()

        if(self.check == 1):
            if((self.time_next-self.time) <= 0.85): 
               if(((time.time()-self.time_next) >= 0.5) and ((self.time_next-self.time) >= 0.4)):
                   self.check = 0
                   self.peak = 0
               
                   self.heartrate = self.time_next - self.time
                   print('heartrate: '+str((1/self.heartrate*60)))
               
                   self.heartrate_ar.append((1/self.heartrate*60))
                   print('heartrate_average: '+str(np.mean(self.heartrate_ar)))
               
            if((self.time_next-self.time) > 0.85):
                self.check = 0
                self.peak = 0
                self.time = 0
                
#initial
fig, (ax,ax2,ax3,ax4) = plt.subplots(4,1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
line3, = ax3.plot(np.random.randn(100))
line4, = ax4.plot(np.random.randn(100))
plt.show(block = False)
plt.setp(line2,color = 'r')
fs = 500

PData= PlotData(500)
ax.set_ylim(300,400)
ax2.set_ylim(-20,20)
ax3.set_ylim(0,400)
ax4.set_ylim(300,400)

# plot parameters
print ('plotting data...')
# open serial port
strPort='com3'
ser = serial.Serial(strPort, 115200)
ser.flush()


#figure z_domain
b = [1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7]
a = [1, 0, 0, 0, 0, 0, 0]

p = np.roots(a)
z = np.roots(b)

angle = np.linspace(-np.pi, np.pi, 50)
cirx = np.sin(angle)
ciry = np.cos(angle)
plt.figure(figsize=(8,8))
plt.plot(cirx, ciry,'k-')
plt.plot(np.real(z), np.imag(z), 'o', markersize=12)
plt.plot(np.real(p), np.imag(p), 'x', markersize=12)
plt.text(0.1, 0.1, len(p), fontsize=12)

plt.grid()

plt.xlim((-2, 2))
plt.xlabel('Real')
plt.ylim((-2, 2))
plt.ylabel('Imag')
    
    
start = time.time()
while True:
    
    for ii in range(10):

        try:
            data = float(ser.readline())       
            PData.add(time.time() - start, data)
            PData.heart_rate(data)
        except:
            pass
        

    #figure2 cal
    PData.axis_yf = np.fft.fft(PData.axis_y)
    PData.axis_yf[0] = 0
    PData.axis_y2 = np.fft.ifft(PData.axis_yf)
    
    #figure3 cal
    w_hat = np.arange(0, 2*np.pi, 2*np.pi/(fs))
    f_analog = w_hat/(2*np.pi) * fs
    
    #figure4 cal
    FIR_y = signal.lfilter([1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7], 1, PData.axis_y)
      
    #set x limits
    ax.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
    ax2.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
    ax3.set_xlim(0,100)
    ax4.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
    
    #set y limits
    ax.set_ylim(min(PData.axis_y)-5,max(PData.axis_y)+5)
    ax2.set_ylim(min(PData.axis_y2)-5,max(PData.axis_y2)+5)
    ax3.set_ylim(0,max(PData.axis_yf)+200)
    ax4.set_ylim(max(FIR_y)-10,max(FIR_y)+5)
    
    #figure1
    line.set_xdata(PData.axis_x)
    line.set_ydata(PData.axis_y)
    
    #figure2
    line2.set_xdata(PData.axis_x)
    line2.set_ydata(PData.axis_y2)
    
    #figure3
    if(len(PData.axis_yf)==500):
        line3.set_xdata(f_analog)
        line3.set_ydata(abs(PData.axis_yf))
        
    #figure4  
    line4.set_xdata(PData.axis_x)
    line4.set_ydata(FIR_y)
       
    fig.canvas.draw()
    fig.canvas.flush_events()