import pyaudio
import numpy as np
<<<<<<< Updated upstream
import keyboard  #new varaible
=======
import keyboard  # new variable
>>>>>>> Stashed changes

# Configuration
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = 2
CHUNK = 1024
volume_threshold = 1000  # initial volume threshold

def estimate_doa(audio_data, threshold):
    mic_channels = audio_data[:, 1:5]
    intensities = np.sum(np.abs(mic_channels), axis=0)

    # Check if the highest intensity is above the threshold
    if np.max(intensities) < threshold:
        return None
    loudest_mic_index = np.argmax(intensities)
    return loudest_mic_index + 2

# Initialize PyAudio
p = pyaudio.PyAudio() #add backround noise here

# Open stream
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
        # Adjust threshold with keyboard input
        if keyboard.is_pressed('up'):
            volume_threshold += 100
            print(f"Volume threshold increased to: {volume_threshold}")
        elif keyboard.is_pressed('down'):
            volume_threshold -= 100
            print(f"Volume threshold decreased to: {volume_threshold}")

        data = stream.read(CHUNK)
        npdata = np.frombuffer(data, dtype=np.int16).reshape(-1, RESPEAKER_CHANNELS)
        mic_index = estimate_doa(npdata, volume_threshold)

        if mic_index is not None:
            print(f"Direction of arrival: Microphone Channel {mic_index}")
        else:
            print("Sound below threshold")

except KeyboardInterrupt:
    print("* done listening")

# Close the stream
stream.stop_stream()
stream.close()
p.terminate()
