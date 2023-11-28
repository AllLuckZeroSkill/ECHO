#DOA algo. by using volume
import pyaudio
import numpy as np

# Configuration
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6  # 6 channels for Respeaker
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = 2  # Replace with your device id
CHUNK = 1024

def estimate_doa(audio_data):
    """
    Estimates the direction of arrival by comparing the intensity of audio from each microphone on the Respeaker.
    :param audio_data: A numpy array where each column represents audio data from one channel of the Respeaker.
                       Channels 2 to 5 correspond to the four microphones.
    :return: Index of the microphone with the highest intensity, corresponding to channels 2 to 5.
    """
    # Consider only channels 2 to 5 for the microphones
    mic_channels = audio_data[:, 1:5]  # assuming channels are 0-indexed

    # Calculate the intensity for each microphone's channel
    intensities = np.sum(np.abs(mic_channels), axis=0)

    # Find the index of the microphone with the highest intensity
    loudest_mic_index = np.argmax(intensities)

    # Adjust the index to correspond to the actual microphone numbers (2 to 5)
    return loudest_mic_index + 2  # +2 because we're starting from channel 2

# Initialize PyAudio
p = pyaudio.PyAudio()

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
        # Read data from audio stream
        data = stream.read(CHUNK)
        # Convert data to numpy array
        npdata = np.frombuffer(data, dtype=np.int16).reshape(-1, RESPEAKER_CHANNELS)
        # Estimate DoA
        mic_index = estimate_doa(npdata)
        print(f"Direction of arrival: Microphone Channel {mic_index}")

except KeyboardInterrupt:
    print("* done listening")

# Close the stream
stream.stop_stream()
stream.close()
p.terminate()
