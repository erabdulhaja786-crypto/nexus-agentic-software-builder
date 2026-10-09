import os
from dotenv import load_dotenv
from groq import Groq

# Load variables from .env
load_dotenv()

# Get Groq API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

# Create Groq client
client = Groq(api_key=api_key)

# Send request to LLM
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "Explain Artificial Intelligence in one simple sentence."
        }
    ],
)

# Print response
print("\n===== GROQ RESPONSE =====\n")
print(response.choices[0].message.content)