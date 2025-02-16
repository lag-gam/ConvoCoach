import os
import time
import wave
import assemblyai as aai
from dotenv import load_dotenv

# Load API Key
load_dotenv(".env")
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

if not aai.settings.api_key:
    raise ValueError("AssemblyAI API key is missing. Make sure it's set in .env1!")

# Audio Configuration
RATE = 16000  # Sample rate
CHANNELS = 1  # Mono
RECORD_SECONDS = 15  # Duration to record


def record_audio():
    """Records audio from the microphone and saves it as a WAV file."""
    import pyaudio

    filename = f"user_audios/recorded_audio_{int(time.time())}.wav"

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

    os.makedirs("user_audios", exist_ok=True)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return filename  # Return the filename for processing


def transcribe_audio(audio_file):
    """
    Transcribes the given audio file and returns the transcript + sentiment analysis.
    
    :param audio_file: Path to the audio file to transcribe.
    :return: A dictionary containing transcription text and sentiment analysis results.
    """
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(sentiment_analysis=True)
    
    transcript = transcriber.transcribe(audio_file, config)
    try:
        os.remove(audio_file)
    except Exception as e:
        print(f"Error deleting file: {e}")

    return {
        "text": transcript.text,
        "sentiment_analysis": [
            {
                "text": result.text,
                "sentiment": result.sentiment,
                "confidence": result.confidence,
                "start": result.start,
                "end": result.end
            }
            for result in transcript.sentiment_analysis
        ]
    }


# Allow this script to be run standalone for testing
if __name__ == "__main__":
    audio_file = record_audio()
    print("Transcribing and analyzing sentiment...")
    result = transcribe_audio(audio_file)

    print("\nTranscription:")
    print(result["text"])

    print("\nSentiment Analysis Results:")
    for entry in result["sentiment_analysis"]:
        print(f"Text: {entry['text']}")
        print(f"Sentiment: {entry['sentiment']}")
        print(f"Confidence: {entry['confidence']}")
        print(f"Timestamp: {entry['start']} - {entry['end']}\n")
