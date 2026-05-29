from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/")
def home():
    return PlainTextResponse(
        content='{"status": "ReceptionAI is running"}',
        headers={"ngrok-skip-browser-warning": "true"}
    )

@app.post("/voice")
async def voice(request: Request):
    response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hi! Thank you for calling. This is Reception AI, your virtual receptionist. Are you calling to make a booking today?</Say>
</Response>"""
    return PlainTextResponse(
        content=response,
        media_type="application/xml",
        headers={"ngrok-skip-browser-warning": "true"}
    )

@app.get("/test-ai")
def test_ai():
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": "You are a friendly medical receptionist at a NZ GP clinic. Greet a patient calling the clinic."
        }]
    )
    return {"response": response.choices[0].message.content}