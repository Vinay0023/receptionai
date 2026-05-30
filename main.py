from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = []

doctor_schedule = {
    "monday": ["9:00am", "10:00am", "2:00pm", "3:00pm"],
    "tuesday": ["9:00am", "11:00am", "1:00pm", "4:00pm"],
    "wednesday": ["10:00am", "11:00am", "2:00pm"],
    "thursday": ["9:00am", "10:00am", "3:00pm", "4:00pm"],
    "friday": ["9:00am", "11:00am", "1:00pm", "2:00pm"],
    "saturday": [],
    "sunday": []
}

def check_availability(day: str, time: str) -> bool:
    day = day.lower()
    if day in doctor_schedule:
        return time.lower() in doctor_schedule[day]
    return False

@app.get("/")
def home():
    return PlainTextResponse(
        content='{"status": "ReceptionAI is running"}',
        headers={"ngrok-skip-browser-warning": "true"}
    )

@app.post("/voice")
async def voice(request: Request):
    conversation_history.clear()
    response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/handle-response" timeout="3" speechTimeout="2" language="en-NZ">
        <Say voice="alice">Good morning! Thank you for calling City Medical. How can I help you today?</Say>
    </Gather>
</Response>"""
    return PlainTextResponse(
        content=response,
        media_type="application/xml",
        headers={"ngrok-skip-browser-warning": "true"}
    )

@app.post("/handle-response")
async def handle_response(SpeechResult: str = Form(None)):
    caller_said = SpeechResult or "hello"

    print(f"Caller said: {caller_said}")

    conversation_history.append({
        "role": "user",
        "content": caller_said
    })

    ai_response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=150,
        messages=[
            {
                "role": "system",
                "content": f"""You are a friendly medical receptionist 
                at a NZ GP clinic called City Medical.
                The doctor is Dr Steven.
                
                Follow this exact flow:
                1. If patient wants to book, ask for their name
                2. Ask for their date of birth
                3. Ask what day they would like to book
                4. Ask what time they would like
                5. Check if Dr Steven is available using this schedule:
                   {doctor_schedule}
                6. If available say: "Great! I have booked you in with 
                   Dr Steven on [day] at [time]. You will receive a 
                   confirmation shortly. Is there anything else I can 
                   help you with?"
                7. If not available say: "I'm sorry, Dr Steven is not 
                   available at that time. The available times on [day] 
                   are [list times]. Which would you prefer?"
                
                Rules:
                - Keep responses short and clear
                - This is a phone call so be conversational
                - Be warm and professional
                - Never give medical advice
                - If patient mentions emergency say: 
                  "Please hang up and call 111 immediately"
                - Saturday and Sunday Dr Steven is not available"""
            }
        ] + conversation_history
    )

    bot_reply = ai_response.choices[0].message.content

    print(f"Bot replied: {bot_reply}")

    conversation_history.append({
        "role": "assistant",
        "content": bot_reply
    })

    response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/handle-response" timeout="3" speechTimeout="2" language="en-NZ">
        <Say voice="alice">{bot_reply}</Say>
    </Gather>
</Response>"""

    return PlainTextResponse(
        content=response,
        media_type="application/xml",
        headers={"ngrok-skip-browser-warning": "true"}
    )

@app.get("/test-ai")
def test_ai():
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=150,
        messages=[{
            "role": "user",
            "content": "You are a friendly medical receptionist at a NZ GP clinic. Greet a patient calling the clinic."
        }]
    )
    return {"response": response.choices[0].message.content}