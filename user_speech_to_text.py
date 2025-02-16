import os
import time
import wave
import requests
import assemblyai as aai
from dotenv import load_dotenv
import time

# Load API Key
load_dotenv(".env1")
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

if not aai.settings.api_key:
    raise ValueError("AssemblyAI API key is missing. Make sure it's set in .env1!")

# Audio Configuration
RATE = 16000  # Sample rate
CHANNELS = 1  # Mono
RECORD_SECONDS = 15  # Duration to record
WAVE_OUTPUT_FILENAME = "user_audios/recorded_audio"+str(time.time())+".wav"

# Record audio from the microphone and save to a WAV file
def record_audio():
    import pyaudio

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=1024)

    print(f"Recording for {RECORD_SECONDS} seconds...")
    frames = []

    for _ in range(0, int(RATE / 1024 * RECORD_SECONDS)):
        data = stream.read(1024)
        frames.append(data)

    print("Recording complete.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# Transcribe the audio file with sentiment analysis
def transcribe_audio(audio_url):
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(sentiment_analysis=True)
    transcript = transcriber.transcribe(audio_url, config)
    return transcript

# Main function
if __name__ == "__main__":
    record_audio()
    audio_url = WAVE_OUTPUT_FILENAME
    print("Transcribing and analyzing sentiment...")
    transcript = transcribe_audio(audio_url)

    print("\nTranscription:")
    print(transcript.text)

    print("\nSentiment Analysis Results:")
    for result in transcript.sentiment_analysis:
        print(f"Text: {result.text}")
        print(f"Sentiment: {result.sentiment}")
        print(f"Confidence: {result.confidence}")
        print(f"Timestamp: {result.start} - {result.end}\n")
