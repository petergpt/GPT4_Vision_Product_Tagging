import os
import openai
import base64
import requests
import json
from prompts import products

# Function to encode a single image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Set the OpenAI API key from environment variables
openai.api_key = os.environ['OPENAI_API_KEY']

# Filename to save responses
filename = 'responses.json'

# Function to save response content
def save_response_content(image_name, content):
    data = {
        "image": image_name,
        "response_content": content
    }

    # Check if file exists and has content
    try:
        with open(filename, 'r+') as file:
            # Read current data from file
            file_data = json.load(file)
            # Append new data
            file_data.append(data)
            # Set file's current position at offset
            file.seek(0)
            # Update JSON file
            json.dump(file_data, file, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create new file with initial data
        with open(filename, 'w') as file:
            json.dump([data], file, indent=4)

# Image path
image_path = "Products/doll.jpg"
base64_image = encode_image(image_path)

# Prepare the image content for payload
image_content = {
    "type": "image_url",
    "image_url": {
        "url": f"data:image/jpeg;base64,{base64_image}"
    }
}


# The text content remains the same
text_content = {
    "type": "text",
    "text": products
}

# Combine the text content with the image contents
combined_contents = [text_content] + [image_content]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai.api_key}"
}

payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
            "role": "user",
            "content": combined_contents
        }
    ],
    "max_tokens": 4000
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

# Check if the response was successful
if response.status_code == 200:
    response_json = response.json()
    try:
        content = response_json['choices'][0]['message']['content']
        print(content)

        # Save the 'content' part of the response along with the image name
        save_response_content(image_path, content)

        print(f"Response content saved to '{filename}'.")

    except KeyError:
        print("The 'choices' key is missing in the response. Full response:")
        print(response_json)
else:
    print(f"Failed to get a successful response. Status code: {response.status_code}")
    print("Full response:")
    print(response.text)