import numpy as np
import pyaudio
import tkinter as tk
from threading import Thread
from scipy.signal import firwin, lfilter

# Configuration for audio input and processing
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = 2  # Make sure this matches your audio device index
CHUNK = 1024
initial_volume_threshold = 20000  # Initial volume threshold to detect sound

# Filter Design Parameters
num_taps = 101  # Number of taps in the FIR filter for signal processing
low_cutoff_freq = 50  # Low cutoff frequency in Hz for the filter
high_cutoff_freq = 1000  # High cutoff frequency in Hz for the filter
nyquist_rate = RESPEAKER_RATE / 2
# Creating the FIR filter
b = firwin(num_taps, [low_cutoff_freq / nyquist_rate, high_cutoff_freq / nyquist_rate], pass_zero=False)

# Function to estimate the direction of arrival (DOA) of sound
def estimate_doa(audio_data):
    mic_channels = audio_data[:, 1:5]  # Using middle 4 channels for DOA estimation
    intensities = np.sum(np.abs(mic_channels), axis=0)
    max_intensity = np.max(intensities)
    normalized_intensities = intensities / max_intensity if max_intensity > 0 else intensities
    print(normalized_intensities)
    loudest_mic_index = np.argmax(intensities)
    return loudest_mic_index + 1  # Adjust to match microphone channel indexing

# Main loop for processing audio input
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
                filtered_data = np.copy(npdata)  # Create a copy for filtering
                for i in range(RESPEAKER_CHANNELS):
                    filtered_data[:, i] = lfilter(b, 1, npdata[:, i])
                mic_index = estimate_doa(filtered_data)
                print(f"Direction of arrival: Microphone Channel {mic_index}")
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
