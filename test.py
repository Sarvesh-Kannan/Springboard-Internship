from google import genai
import os

# Make sure your API key is set in environment
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

resp = client.models.generate_content(
    model="gemini-flash-latest",
    contents="Reply with OK"
)
print(resp.text)
