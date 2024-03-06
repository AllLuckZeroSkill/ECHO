from tuning import Tuning
import usb.core
import usb.util
import numpy as np
import matplotlib.pyplot as pyplot
from gpiozero import PWMOutputDevice
from time import sleep
from i2c_hapticmotordriver import HapticMotorDriver 

import smbus
import time

class TCA9548:
    def __init__(self, address=0x70, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)
        self.channels = 8

    def select_channel(self, channel):
        """Selects a single channel."""
        if channel >= self.channels:
            raise ValueError("Channel must be 0-7")
        self.bus.write_byte(self.address, 1 << channel)
    
    def disable_all_channels(self):
        """Disables all channels."""
        self.bus.write_byte(self.address, 0x00)

# Example usage
if __name__ == "__main__":
    mux = TCA9548()
    
    try:
        # Select channel 3
        mux.select_channel(2)
        print("Channel 3 selected.")
        # Add your I2C communication code here to communicate with devices on channel 3
        hap = HapticMotorDriver()
        hap.set_vibration(50)
    except Exception as e:
        print(e)
    finally:
        time.sleep(2)
        hap.set_vibration(0)
        # Disable all channels when done
       # mux.disable_all_channels()
        print("All channels disabled.")

    try:
        # Select channel 3
        mux.select_channel(3)
        print("Channel 3 selected.")
        # Add your I2C communication code here to communicate with devices on channel 3
        hap = HapticMotorDriver()
        hap.set_vibration(50)
    except Exception as e:
        print(e)
    finally:
        time.sleep(2)
        hap.set_vibration(0)
        # Disable all channels when done
       # mux.disable_all_channels()
        print("All channels disabled.")
        


#
    




