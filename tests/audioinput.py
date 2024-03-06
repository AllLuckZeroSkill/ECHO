import pyaudio
import numpy as np
import wave

# Configuration
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = 2
CHUNK = 1024
RECORD_SECONDS = 10
file_number = 1  # Start with audio file 'audio1.wav'

def record_audio(file_number):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=p.get_format_from_width(RESPEAKER_WIDTH),
        channels=RESPEAKER_CHANNELS,
        rate=RESPEAKER_RATE,
        input=True,
        input_device_index=RESPEAKER_INDEX,
        frames_per_buffer=CHUNK
    )
    
    print(f"* Recording audio{file_number}.wav")
    frames = []
    
    for _ in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the recorded data as a WAV file
    wf = wave.open(f'audio{file_number}.wav', 'wb')
    wf.setnchannels(RESPEAKER_CHANNELS)
    wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
    wf.setframerate(RESPEAKER_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"* Done recording audio{file_number}.wav")

while True:
    record_audio(file_number)
    file_number += 1  # Increment the file number for the next recording
    input("Press Enter to record another 10-second audio file or Ctrl+C to stop...")
