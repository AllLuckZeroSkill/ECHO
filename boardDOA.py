from tuning import Tuning
import usb.core
import usb.util
import numpy as np
import matplotlib.pyplot as pyplot
from gpiozero import PWMOutputDevice
from time import sleep
from i2c_hapticmotordriver import HapticMotorDriver as hap
import INA219

# Initialize GPIO for the motor
#motor = PWMOutputDevice(14)

# Initialize the Haptic Motor Driver
hap_driver = HapticMotorDriver()  # Correctly instantiate the driver

# USB device setup for microphone
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

# Creates an INA219 instance to get battery data
ina219 = INA219(addr=0x43)

if dev:
    Mic_tuning = Tuning(dev)

    # Initialize the plot
    fig1 = pyplot.figure()
    Polar_Graph = fig1.add_subplot(111, projection='polar')
    Polar_Graph.set_rticks([1])  # Aesthetic radius ticks
    Polar_Graph.set_title("Mic_tuning.direction Location", va='bottom')

    while True:
        try:
            direction = Mic_tuning.direction
            print(direction)  # Prints angle of direction of sound
            
            # Vibrate motor based on direction
            if 90 < direction < 180:
                hap_driver.set_vibration(127)  # Corrected method call
            else:
                hap_driver.set_vibration(0)  # Corrected method call
        
            # Clear the plot and redraw
            Polar_Graph.clear()
            Polar_Graph.set_rticks([1])
            theta = np.radians(direction)  # More precise conversion
            Polar_Graph.scatter([theta], [1], c='r')
            Polar_Graph.set_title("Mic_tuning.direction Location", va='bottom')

            pyplot.draw()
            pyplot.pause(0.1)  # Adjust as necessary

            '''
            # if phone application battery state button pressed: #pseudo code placeholder for the phone application input
            bus_voltage = ina219.getBusVoltage_V()                   # voltage on V- (load side)
            print("Load Voltage:  {:6.3f} V".format(bus_voltage))    # what it looks like to print the load voltage, width is 6, the precision is 3 decimals, f is for floating point
            current = ina219.getCurrent_mA()                         # current in mA
            print("Current:       {:6.3f} A".format(current/1000))   # what it looks like to print the current
            power = ina219.getPower_W()                              # power in W
            print("Power:         {:6.3f} W".format(power))          # printing the power
            percent = (bus_voltage - 3)/1.2*100                      # battery percentage 
            if(percent > 100):percent = 100                          # percent of battery can not be over 100%
            if(percent < 0):percent = 0                              # percent of battery can not be under 0%
            print("Percent:       {:3.1f}%".format(percent))
            '''
            
        except KeyboardInterrupt:
          #  motor.value = 0  # Ensure motor is turned off when exiting
            break
