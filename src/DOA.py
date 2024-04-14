import numpy as np
import tkinter as tk
import pyaudio
from threading import Thread
from scipy.signal import firwin, lfilter
from lib.tuning import Tuning
import usb.core
import usb.util
from lib.i2c_hapticmotordriver import HapticMotorDriver
from lib.i2c_multiplexer import TCA9548
import time

# Configuration for audio input and processing
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = 2  # Audio device index
CHUNK = 1024
initial_volume_threshold = 20000  # Initial volume threshold to detect sound
direction_count_threshold = 5  # Threshold for the number of times a direction can be the loudest before pausing

# Filter Design Parameters
num_taps = 101  # Number of taps in the FIR filter
low_cutoff_freq = 50  # Low cutoff frequency in Hz
high_cutoff_freq = 1000  # High cutoff frequency in Hz
nyquist_rate = RESPEAKER_RATE / 2
b = firwin(num_taps, [low_cutoff_freq / nyquist_rate, high_cutoff_freq / nyquist_rate], pass_zero=False)

# USB device setup for microphone
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
if dev:
    Mic_tuning = Tuning(dev)

direction_counts = [0] * 6  # Array to keep track of direction loudness counts

def activate_vibration_motors(motor_index, intensity, count):
    channel = motor_index + 2
    mux = TCA9548()
    hap = HapticMotorDriver()

    try:
        mux.select_channel(channel)
        print(f"Channel {channel} selected.")

        if count >= direction_count_threshold:
            print("Pausing vibration due to continuous high intensity in one direction.")
            hap.init()
            hap.set_vibration(0)  # Stop the vibration
            time.sleep(1)  # Pause for a duration to avoid motor wear and user discomfort
        else:
            # Calculate scaled intensity based on the full range mapped to 0-127
            scaled_intensity = int((intensity / 1000000) * 127)
            vibrationPower = max(0, min(127, scaled_intensity))
            hap.init() # Bring up to Mark
            hap.set_vibration(vibrationPower)
            time.sleep(0.1)
            print(f"Motor on channel {channel} set to vibration power {vibrationPower}.")

    except Exception as e:
        print(e)
    finally:
        # Always ensure to disable all channels to prevent leakage or unintended behavior
        hap.set_vibration(0)
        mux.disable_all_channels()
        print("All channels disabled.")


def estimate_doa(audio_data):
    if Mic_tuning:
        return Mic_tuning.direction
    else:
        return "Device not connected"

def audio_stream_loop(volume_threshold):
    p = pyaudio.PyAudio()
    stream = p.open(
        rate=RESPEAKER_RATE,
        format=p.get_format_from_width(RESPEAKER_WIDTH),
        channels=RESPEAKER_CHANNELS,
        input=True,
        input_device_index=RESPEAKER_INDEX,
        frames_per_buffer=CHUNK
    )
    print("* listening")
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            npdata = np.frombuffer(data, dtype=np.int16).reshape(-1, RESPEAKER_CHANNELS)
            initial_intensities = np.sum(np.abs(npdata[:, 1:5]), axis=0)

            if np.max(initial_intensities) >= volume_threshold.get():
                direction = estimate_doa(npdata)
                motor_index = int((direction + 30) // 60) % 6
                direction_counts[motor_index] += 1
                print(f"Direction of arrival: {direction} degrees, motor index: {motor_index+2}, count: {direction_counts[motor_index]}")
                activate_vibration_motors(motor_index, initial_intensities, direction_counts[motor_index])
    except KeyboardInterrupt:
        print("* done listening")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# Setting up the GUI for threshold control
root = tk.Tk()
root.title("Volume Threshold Control")
volume_threshold = tk.IntVar(value=initial_volume_threshold)
threshold_slider = tk.Scale(root, from_=18000, to=500000, orient='horizontal', label='Volume Threshold', variable=volume_threshold)
threshold_slider.pack()

# Starting the audio stream in a separate thread
audio_thread = Thread(target=audio_stream_loop, args=(volume_threshold,))
audio_thread.daemon = True
audio_thread.start()

# Start the GUI event loop
root.mainloop()
