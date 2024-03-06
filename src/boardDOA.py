from lib.tuning import Tuning
import usb.core
import usb.util
import numpy as np
import matplotlib.pyplot as pyplot
from gpiozero import PWMOutputDevice
from time import sleep
from lib.i2c_hapticmotordriver import HapticMotorDriver

# Initialize the Haptic Motor Driver
#hap_driver = HapticMotorDriver()  # Correctly instantiate the driver

# USB device setup for microphone
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

if dev:
    Mic_tuning = Tuning(dev)
    """ UNCOMMENT FOR VISUALIZED GRAPH (1)
    # Initialize the plot
    fig1 = pyplot.figure()
    Polar_Graph = fig1.add_subplot(111, projection='polar')
    Polar_Graph.set_rticks([1])  # Aesthetic radius ticks
    Polar_Graph.set_title("Mic_tuning.direction Location", va='bottom')
    """
    while True:
        try:
            direction = Mic_tuning.direction
            print(direction)  # Prints angle of direction of sound
            
            # Vibrate motor based on direction
            if 90 < direction < 180:
                print("Vibrate")
                #Uncomment below for vibration
                #hap_driver.set_vibration(127)  # Corrected method call
            else:
                print("")
                #hap_driver.set_vibration(0)  # Corrected method call
                
            """UNCOMMENT FOR VISUALIZED GRAPH (2)
            # Clear the plot and redraw
            Polar_Graph.clear()
            Polar_Graph.set_rticks([1])
            theta = np.radians(direction)  # More precise conversion
            Polar_Graph.scatter([theta], [1], c='r')
            Polar_Graph.set_title("Mic_tuning.direction Location", va='bottom')

            pyplot.draw()
            pyplot.pause(0.1)  # Adjust as necessary
            """
        except KeyboardInterrupt:
          #  motor.value = 0  # Ensure motor is turned off when exiting
            break
