
### AI Voice Receptionist for NZ GP Clinics

---

##  About Me

Hi! I'm Vinay, based in Wellington, NZ.
I hold a Level 6 Diploma in Cyber Security and a 
Level 7 Diploma in Cloud Engineering, along with 
AWS Cloud Practitioner and AWS AI Cloud Practitioner 
certifications. I'm currently working towards my 
AWS Solutions Architect Associate.

I built ReceptionAI as a hands-on project to combine 
my cloud skills with AI engineering and solve a real 
problem I noticed in NZ healthcare.

Currently looking for Junior Cloud Engineer or 
AI Engineer roles anywhere in NZ or Australia.

---

## Why I Built This

While living in Wellington I noticed something 
simple but frustrating, GP clinics miss calls 
every single day.

When a receptionist is busy, the next patient 
hits voicemail. This is especially hard for 
elderly patients who get confused by voicemail 
systems and just hang up.

The clinic loses patient satisfaction over 
something that technology can easily solve.
So I built ReceptionAI.

---

##  What It Does

ReceptionAI is an AI receptionist that:
- Answers calls instantly when staff are busy
- Has a natural two way conversation with patients
- Collects patient name and date of birth
- Checks doctor availability
- Books appointments automatically
- Works 24/7 including after hours
- Detects emergencies and advises to call 111

Staff get to focus on patients in front of them.
Elderly patients get helped immediately.
No more voicemail confusion.

---

##  Architecture
Patient calls clinic
↓
Twilio receives call
↓
Groq AI understands conversation
↓
FastAPI backend processes response
↓
Bot speaks back to patient
↓
Booking saved to AWS RDS PostgreSQL
↓
Email confirmation via AWS SES
↓
Staff alerted via AWS SNS

---

## Demo

Live URL: http://3.106.124.135:8000

Sally is currently running 24/7 on AWS EC2.
NZ phone number activation in progress.
Demo video coming soon.

##  Tech Stack
- **Language:** Python
- **Framework:** FastAPI
- **Calls:** Twilio
- **AI Brain:** Groq API (Llama 3)
- **Voice:** AWS Polly
- **Transcription:** AWS Transcribe
- **Database:** AWS RDS PostgreSQL
- **Hosting:** AWS EC2
- **Emails:** AWS SES
- **Alerts:** AWS SNS
- **Scheduling:** AWS EventBridge
- - **Hosting:** AWS EC2 Live at http://3.106.124.135:8000

---

##  Features
- Answers inbound calls when receptionist is busy
- Natural two way voice conversation
- Collects patient name and date of birth
- Checks real doctor availability
- Books appointments automatically
- 24/7 availability including after hours
- Emergency detection — advises to call 111
- Daily email summary to clinic manager

---

##  Current Progress

- Bot answers inbound calls (Done)
- Two way voice conversation (Done)
- Collects patient name and DOB (Done)
- Checks doctor availability (Done)
- Books appointments automatically (Done)
- Saves bookings to AWS RDS PostgreSQL (Done)
- AWS SES email confirmations (Done)
- Deployed AWS EC2 (Done)
- Audio Storage:AWS S3(Done)
- AWS Polly neural voice (In Progress)
- Interruption handling (Coming Soon)
- Google Calendar integration (Coming Soon)

---

##  Certification

- **Level 7 Diploma in Cloud Engineering
- **Level 6 Diploma in Cyber Security
- **AWS Cloud Practitioner
- **AWS AI Cloud Practitioner
- **AWS Solutions Architect Associate** (In Progress)

---

##  Contact

**Vinay Sharma**
Wellington, NZ
Open to roles anywhere in NZ or Australia

🔗 [LinkedIn](https://www.linkedin.com/in/vinaysharma2323/)
📧 sharmavinay2323@gmail.com

---



