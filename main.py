from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from groq import Groq
from dotenv import load_dotenv
import os
import psycopg2
from datetime import datetime

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

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    return conn

def create_bookings_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                patient_name VARCHAR(100),
                date_of_birth VARCHAR(50),
                booking_day VARCHAR(50),
                booking_time VARCHAR(50),
                doctor VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Bookings table ready!")
    except Exception as e:
        print(f"❌ Database error: {e}")

def save_booking(patient_name, date_of_birth, booking_day, booking_time, doctor):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings 
            (patient_name, date_of_birth, booking_day, booking_time, doctor)
            VALUES (%s, %s, %s, %s, %s)
        """, (patient_name, date_of_birth, booking_day, booking_time, doctor))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Booking saved for {patient_name}")
    except Exception as e:
        print(f"❌ Error saving booking: {e}")

# Create table when app starts
create_bookings_table()

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
                
                IMPORTANT: When booking is confirmed include this exact 
                format in your response:
                BOOKING_CONFIRMED|name|dob|day|time|Dr Steven
                
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

    # Check if booking was confirmed and save to database
    if "BOOKING_CONFIRMED|" in bot_reply:
        try:
            parts = bot_reply.split("BOOKING_CONFIRMED|")[1].split("|")
            save_booking(
                patient_name=parts[0],
                date_of_birth=parts[1],
                booking_day=parts[2],
                booking_time=parts[3],
                doctor=parts[4].split("\n")[0]
            )
            bot_reply = bot_reply.replace(
                bot_reply[bot_reply.find("BOOKING_CONFIRMED"):], ""
            ).strip()
        except Exception as e:
            print(f"Error parsing booking: {e}")

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

@app.get("/bookings")
def get_bookings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings ORDER BY created_at DESC")
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"bookings": bookings}
    except Exception as e:
        return {"error": str(e)}

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