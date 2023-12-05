#DOA algo. directly imported from Respeakers libraries
from tuning import Tuning
import usb.core
import usb.util
import time
import numpy as np
import matplotlib.pyplot as pyplot

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

if dev:
    Mic_tuning = Tuning(dev)
    print (Mic_tuning.direction)
    while True:
        try:
            print (Mic_tuning.direction) #Prints angle of direction of sound
            
            #This Section Is For The Graph
            theta = (float(Mic_tuning.direction)/180*np.pi) #Takes the Mic_tuning.direction and converts it to a usable theta value
            radius = [1] #Radius is always 1 for visual aesthetics
            fig1 = pyplot.figure()
            Polar_Graph = fig1.add_subplot(111, projection='polar')
            Polar_Graph.set_rticks([1])  # This Limits The Text On The Radius For Visual Aesthetics
            Polar_Graph.scatter(theta,radius, c ='r') #Plots The Point
            Polar_Graph.set_title("Mic_tuning.direction Location", va='bottom') #Adds Title Information
            pyplot.show() #Shows the graph
            
            time.sleep(1)
        except KeyboardInterrupt:
            break
