from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from groq import Groq
from dotenv import load_dotenv
import os
import psycopg2
import boto3
from datetime import datetime

load_dotenv()

app = FastAPI()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ses_client = boto3.client(
    'ses',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

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
        port=os.getenv("DB_PORT"),
        connect_timeout=10
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
        return True
    except Exception as e:
        print(f"❌ Error saving booking: {e}")
        return False

def send_patient_email(patient_name, booking_day, booking_time, doctor):
    try:
        ses_client.send_email(
            Source=os.getenv("SENDER_EMAIL"),
            Destination={
                'ToAddresses': [os.getenv("CLINIC_EMAIL")]
            },
            Message={
                'Subject': {
                    'Data': f'Appointment Confirmation - City Medical'
                },
                'Body': {
                    'Text': {
                        'Data': f"""Hi {patient_name},

Thank you for calling City Medical.

Your appointment has been confirmed:

Doctor: {doctor}
Day: {booking_day}
Time: {booking_time}
Location: City Medical, Wellington

If you need to cancel or reschedule please call us.

See you soon!

Sally
City Medical Reception"""
                    }
                }
            }
        )
        print(f"✅ Patient email sent for {patient_name}")
    except Exception as e:
        print(f"❌ Email error: {e}")

def send_staff_email(patient_name, date_of_birth, booking_day, booking_time, doctor, transcript):
    try:
        ses_client.send_email(
            Source=os.getenv("SENDER_EMAIL"),
            Destination={
                'ToAddresses': [os.getenv("CLINIC_EMAIL")]
            },
            Message={
                'Subject': {
                    'Data': f'Call Summary - {patient_name} - {booking_day} {booking_time}'
                },
                'Body': {
                    'Text': {
                        'Data': f"""New Booking - Call Summary

Patient Details:
Name: {patient_name}
Date of Birth: {date_of_birth}
Booked: {booking_day} at {booking_time}
Doctor: {doctor}
Call Time: {datetime.now().strftime("%d %B %Y, %I:%M %p")}

Full Conversation Transcript:
{transcript}

This is an automated summary from ReceptionAI.
City Medical, Wellington"""
                    }
                }
            }
        )
        print(f"✅ Staff email sent for {patient_name}")
    except Exception as e:
        print(f"❌ Staff email error: {e}")

create_bookings_table()

SYSTEM_PROMPT = f"""Your name is Sally. You are a receptionist at City Medical in Wellington, NZ. The doctor is Dr Steven.

IMPORTANT RULES:
- Never say you are a bot or AI
- Never say you are automated
- If asked if you are real say: I am Sally from City Medical, how can I help?
- Speak naturally like a real receptionist
- Be warm, friendly and professional
- Keep responses short - this is a phone call

Follow this exact flow:
1. If patient wants to book ask for their name
2. Ask for their date of birth
3. Ask what day they would like
4. Ask what time they would like
5. Check availability using this schedule: {doctor_schedule}
6. If available confirm booking and say: Perfect! I have booked you in with Dr Steven on that day and time. You will receive a confirmation email shortly. Then include: BOOKING_CONFIRMED|name|dob|day|time|Dr Steven
7. If not available offer alternative times

- Never give medical advice
- Emergency: Please hang up and call 111 now
- Saturday and Sunday Dr Steven is not available"""

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
        <Say voice="alice">Good morning! Thank you for calling City Medical. This is Sally speaking, how can I help you today?</Say>
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
                "content": SYSTEM_PROMPT
            }
        ] + conversation_history
    )

    bot_reply = ai_response.choices[0].message.content

    print(f"Sally replied: {bot_reply}")

    if "BOOKING_CONFIRMED|" in bot_reply:
        try:
            parts = bot_reply.split("BOOKING_CONFIRMED|")[1].split("|")
            patient_name = parts[0]
            date_of_birth = parts[1]
            booking_day = parts[2]
            booking_time = parts[3]
            doctor = parts[4].split("\n")[0]

            save_booking(patient_name, date_of_birth, booking_day, booking_time, doctor)

            transcript = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversation_history
            ])

            send_patient_email(patient_name, booking_day, booking_time, doctor)
            send_staff_email(patient_name, date_of_birth, booking_day, booking_time, doctor, transcript)

            bot_reply = bot_reply.replace(
                bot_reply[bot_reply.find("BOOKING_CONFIRMED"):], ""
            ).strip()

        except Exception as e:
            print(f"Error processing booking: {e}")

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
            "content": "You are Sally, a friendly receptionist at City Medical NZ. Greet a patient."
        }]
    )
    return {"response": response.choices[0].message.content}