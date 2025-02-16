import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

import user_speech_to_text as STT #speech to text
import test_speech_analysis as chat_response

# Load environment variables
load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AVATAR_API_KEY = os.getenv("AVATAR_API_KEY")

if not ASSEMBLYAI_API_KEY:
    raise ValueError("Missing AssemblyAI API key in .env!")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key in .env!")
if not AVATAR_API_KEY:
    raise ValueError("Missing D-ID API key in .env!")

app = Flask(__name__)
CORS(app, resources={r"/generate-video": {"origins": "http://localhost:5173"}})




@app.route("/generate-video", methods=["POST"])
def generate_video():
    """
    Endpoint that:
    1. Records + transcribes audio.
    2. Generates GPT-based response.
    3. Creates a D-ID talk (video) with a chosen avatar reading the AI response.
    4. Polls until the video is ready and returns the video URL.
    """
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file uploaded"}), 400

        audio_file = request.files["audio"]
        filename = f"user_audios/uploaded_{int(time.time())}.wav"
        os.makedirs("user_audios", exist_ok=True)  # Ensure directory exists
        audio_file.save(filename)
       
        transcription = STT.transcribe_audio(filename)
        transcript_text = transcription.get("text", "").strip()

        if not transcript_text:
            return jsonify({"error": "No valid transcription received."}), 400


        ai_response = chat_response.generate_avatar_response(transcript_text)
        print("Received AI response:", ai_response)

       
        # Choose your avatar's image URL
        source_url = 'https://media-hosting.imagekit.io//4078ec62a6824c90/screenshot_1739688772692.png?Expires=1834296773&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=LwWvBbL2shd0AqMt~XyVwUwxey2AGKgPPrMEAql3lULNTvG8mF~Urcxhpy7KvW2Cy2LL1VWU69UBsOXc5SWU9FgsvvVz03ggSbtVtApbitZ2eh7uKwiv0rzsvhTFCwmJBxPpiU9D-CdY~ynDhlHodH~xE8wpd2WYAzdChBhLW2QfeEPDs3zP12LXeZFnO0-05Xco0LTnwQOUK12ZDUsIZLtkWIln6Ooqkb9R-BjBDKT9zGnw5IY5D2JHWrTiJOLX3H0W0Ti65BcXYrbYiILndV2xVM-aIfVPoCtz2bYrSPswkG5yPYDErl79jApaQCvIc3mjZBDvCpEjC4u2U-7xGw__'

        # Create talk endpoint
        create_talk_url = "https://api.d-id.com/talks"
        
        # D-ID API uses Basic Auth with your D-ID API key as the "username" and no password
        headers = {
            "Authorization": f"Basic {AVATAR_API_KEY}",
            "Content-Type": "application/json"
        }

        # Payload for creating the talk
        data = {
            "source_url": source_url,
            "script": {
                # Optionally specify voice provider settings here:
                # "provider": {
                #     "type": "amazon",
                #     "voice_id": "Joey"
                # },
                "type": "text",
                "input": ai_response
            }
        }

        # Create the talk
        response = requests.post(create_talk_url, headers=headers, json=data)

        if response.status_code != 201:
            return jsonify({
                "error": f"Failed to create talk: {response.status_code} - {response.text}"
            }), 500

        talk_id = response.json().get("id")
        print(f"Talk created successfully with ID: {talk_id}")

        # ---------------------------
        # Step 4: Poll until video is ready
        # ---------------------------
        get_talk_url = f"https://api.d-id.com/talks/{talk_id}"

        result_url = None
        while True:
            poll_response = requests.get(get_talk_url, headers=headers)
            if poll_response.status_code == 200:
                talk_data = poll_response.json()
                status = talk_data.get("status")
                if status == "done":
                    result_url = talk_data.get("result_url")
                    print(f"Video generated successfully: {result_url}")
                    break
                elif status == "error":
                    return jsonify({"error": "Error in video generation."}), 500
                else:
                    print("Video is still processing...")
            else:
                return jsonify({"error": f"Failed to retrieve talk: {poll_response.status_code} - {poll_response.text}"}), 500

            time.sleep(5)  # Wait 5 seconds before polling again

        # Return the final video link
        return jsonify({
            "transcript": transcript_text,
            "ai_response": ai_response,
            "video_url": result_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run the Flask server
    app.run(port=5000, debug=True)