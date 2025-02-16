import openai
import os
import re
import numpy as np
from dotenv import load_dotenv
import user_speech_to_text

# Load .env for API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Make sure '.env' exists and contains 'OPENAI_API_KEY'.")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

#TODO: Add text speech feedback (num words in response/num_words)
def generate_avatar_response(transcribed_text):
    """
    Uses OpenAI API to analyze speech and provide conversational feedback while keeping the topic in mind.
    """

    prompt = f"""
    Imagine you are a **vocal coach assistant** designed to help a wide variety of users improve their speech clarity while keeping the conversation flowing.
    Your task is to:
    1️⃣ **Analyze the user's speech transcript** and look for:
       - **Unfinished thoughts** (sentences that end abruptly).
       - **Repeated words** (signs of stuttering or hesitation).
       - **Filler words** (uh, um, like, you know, actually, basically, so).
       - **Long pauses** (indicated by "...").
    2️⃣ **Continue the conversation naturally** by responding in a way that keeps the user's topic in mind.
    3️⃣ **Provide subtle, encouraging feedback** in a conversational manner—avoid sounding too robotic or overly critical.

    **Rules for Your Response:**
    - Be **supportive and friendly**.
    - Your response should be **2-3 short sentences**.
    - First, **engage with what the user was trying to say**.
    - Then, **gently provide feedback** to help them improve.
    - Most importantly, only give feedback **when necessary**. If speech was good and coherent, compliment/commend them.
    
    **User's Speech Transcript:**
    "{transcribed_text}"

    Based on this transcript, respond as if you were talking to them in real-time. Keep the conversation flowing while subtly helping them improve.
    """

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,  # Balances structure and variation
        max_tokens=200  # Ensures concise responses
    )

    return response.choices[0].message.content.strip()


# Transcript (Test Case)
def get_response():
    audio_file = user_speech_to_text.record_audio()
    transcript = user_speech_to_text.transcribe_audio(audio_file)
    transcript_text = transcript.get("text", "").strip()

    if not transcript_text:
        print("⚠️ No valid transcription received. Exiting...")
        exit()

    # Get AI avatar response
    avatar_response = generate_avatar_response(transcript_text)
    print(avatar_response)
    return avatar_response
