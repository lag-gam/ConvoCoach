import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file

api_key = os.getenv('AVATAR_API_KEY')
if api_key is None:
    raise ValueError("AVATAR_API_KEY environment variable is not set")


# URL of the avatar image
# source_url = 'https://media-hosting.imagekit.io//4078ec62a6824c90/screenshot_1739688772692.png?Expires=1834296773&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=LwWvBbL2shd0AqMt~XyVwUwxey2AGKgPPrMEAql3lULNTvG8mF~Urcxhpy7KvW2Cy2LL1VWU69UBsOXc5SWU9FgsvvVz03ggSbtVtApbitZ2eh7uKwiv0rzsvhTFCwmJBxPpiU9D-CdY~ynDhlHodH~xE8wpd2WYAzdChBhLW2QfeEPDs3zP12LXeZFnO0-05Xco0LTnwQOUK12ZDUsIZLtkWIln6Ooqkb9R-BjBDKT9zGnw5IY5D2JHWrTiJOLX3H0W0Ti65BcXYrbYiILndV2xVM-aIfVPoCtz2bYrSPswkG5yPYDErl79jApaQCvIc3mjZBDvCpEjC4u2U-7xGw__'
# Henok
source_url = 'https://media-hosting.imagekit.io//b9a94f2580c647be/screenshot_1739696990595.png?Expires=1834304991&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=QoHsh~Mtks6TznmRGXzCjBoPPts-fRoXzjB~3arufkhEKO5eRo2GTIV8teM8PxseAVlYJJcV3am5~397h0K0-CPSzmD6UnkDcvJfpCPoYPzovU3hhWqXbGKD4Q~8YY5GcLwCuYbxiGAThLVqUgonT8tY2EuuE07YQTyM9XUHqJ5OmLauk9ikO~k6bkk1H75DecK0rMMI0CO3oHLs72fvE4LLNzvgIXiTmyzuDC0JxmvdZGsA6oZUghuLxtCGZr8DcvKNGlM~rlCVeGVTHWgl6RluUxrfdxfKXg9jLj7x0GlPia3M~VSkS9MW8C8jnCZJzNXN4msVV5iJh~bT5Tyfdg__'
# Text you want the avatar to speak
text_input = "Hey, great job keeping your stuttering down to zero! Let's work on reducing those long pauses a bit more, but you're definitely on the right track. Keep it up!"

# Endpoint to create a talk
create_talk_url = 'https://api.d-id.com/talks'

# Headers for the request
headers = {
    'Authorization': f'Basic {api_key}',
    'Content-Type': 'application/json'
}

# Data payload for the request
data = {
    'source_url': source_url,
    'script': {
        # "provider": {
        #     "type": "amazon",
        #     "voice_id": "Joey"
        #     },
        'type': 'text',
        'input': text_input
    }
}

response = requests.post(create_talk_url, headers=headers, json=data)

if response.status_code == 201:
    talk_id = response.json().get('id')
    print(f'Talk created successfully with ID: {talk_id}')
else:
    print(f'Failed to create talk: {response.status_code} - {response.text}')
    exit()

# Endpoint to retrieve the generated video
get_talk_url = f'https://api.d-id.com/talks/{talk_id}'


# Polling to check the status of the video generation
while True:
    response = requests.get(get_talk_url, headers=headers)
    if response.status_code == 200:
        talk_data = response.json()
        if talk_data.get('status') == 'done':
            result_url = talk_data.get('result_url')
            print(f'Video generated successfully: {result_url}')
            break
        elif talk_data.get('status') == 'error':
            print('Error in video generation.')
            break
        else:
            print('Video is being processed...')
    else:
        print(f'Failed to retrieve talk: {response.status_code} - {response.text}')
        break
    time.sleep(5)  # Wait for 5 seconds before polling again