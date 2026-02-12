import os
from dotenv import load_dotenv
from openai import OpenAI

# LOAD .env FIRST
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

resp = client.responses.create(
    model="gpt-4.1-mini",
    input="Say hello"
)

print(resp.output_text)
