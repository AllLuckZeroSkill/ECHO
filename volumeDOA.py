import pyaudio
import numpy as np
import tkinter as tk
from threading import Thread

# Configuration
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = 2
CHUNK = 1024
initial_volume_threshold = 20000  # Initial volume threshold

def estimate_doa(audio_data, threshold):
    mic_channels = audio_data[:, 1:5]
    intensities = np.sum(np.abs(mic_channels), axis=0)
    print(intensities)
    # Check if the highest intensity is above the threshold
    if np.max(intensities) < threshold:
        return None
    loudest_mic_index = np.argmax(intensities)
    return loudest_mic_index + 2

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
            data = stream.read(CHUNK)
            npdata = np.frombuffer(data, dtype=np.int16).reshape(-1, RESPEAKER_CHANNELS)
            current_threshold = volume_threshold.get()
            #print(f"Current volume threshold: {current_threshold}")  # Print the slider value
            mic_index = estimate_doa(npdata, current_threshold)

            if mic_index is not None:
                mic_channels = npdata[:, 1:5]
                intensities = np.sum(np.abs(mic_channels), axis=0)
                if np.max(intensities) >= current_threshold:
                    print(f"Direction of arrival: Microphone Channel {mic_index}")

    except KeyboardInterrupt:
        print("* done listening")

    # Close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

# GUI setup
root = tk.Tk()
root.title("Volume Threshold Control")

volume_threshold = tk.IntVar(value=initial_volume_threshold)
threshold_slider = tk.Scale(root, from_=18000, to=500000, orient='horizontal', label='Volume Threshold', variable=volume_threshold)
threshold_slider.pack()

# Start audio stream in a separate thread
audio_thread = Thread(target=audio_stream_loop, args=(volume_threshold,))
audio_thread.daemon = True
audio_thread.start()

# Start the GUI event loop
root.mainloop()
