import openai
import os
import re
import numpy as np
from dotenv import load_dotenv

# Load .env for API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Make sure '.env' exists and contains 'OPENAI_API_KEY'.")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

# Define common filler words
FILLER_WORDS = {"umm", "uh", "like", "you know", "so", "actually", "literally", "basically", "kinda", "sort of"}

def analyze_speech_pattern(transcribed_text, total_duration_seconds):
    """
    Detects filler words, pauses, stuttering, and words per second (WPS).
    """
    words = transcribed_text.split()
    num_words = len(words)

    # Detect repeated words (stuttering)
    repeated_words = [word for i, word in enumerate(words[:-1]) if word == words[i+1]]

    # Detect filler words
    filler_count = sum(1 for word in words if word.lower() in FILLER_WORDS)

    # Detect long pauses ("...", multiple spaces)
    long_pauses = len(re.findall(r"\.\.\.|\s{3,}", transcribed_text))

    # Calculate words per second (WPS)
    wps = round(num_words / total_duration_seconds, 2) if total_duration_seconds > 0 else 0

    # Structured speech analysis
    speech_analysis = f"""
    Words per second: {wps}
    Filler words count: {filler_count}
    Stuttering instances: {len(set(repeated_words))}
    Long pauses detected: {long_pauses}
    """

    return speech_analysis

def generate_avatar_response(transcribed_text, total_duration_seconds):
    """
    Generates a **natural** AI avatar response based on speech analysis.
    """
    speech_analysis = analyze_speech_pattern(transcribed_text, total_duration_seconds)

    prompt = f"""
    You are a friendly AI speaking coach helping someone improve their speech.
    Based on the analysis below, respond in **natural spoken language** as if you were talking to them.
    
    {speech_analysis}

    Your response should be **1-2 short sentences**, casual, supportive, and sound natural.
    """

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,  # Balances structure and variation
        max_tokens=50  # Ensures concise responses
    )

    return response.choices[0].message.content.strip()

# 🔹 Example Whisper-generated Transcript (Test Case)
whisper_transcript = "Umm, umm, so I... I think, that like, uh, we should maybe, umm, go to the store..."
total_speaking_time = 12  # Assume the transcript duration was 12 seconds

# 🔹 Get AI avatar response
avatar_response = generate_avatar_response(whisper_transcript, total_speaking_time)

# 🔹 Print the direct avatar response (no headers, just natural speech)
print(avatar_response)
