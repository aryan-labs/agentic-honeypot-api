from fastapi import FastAPI, Depends
from dotenv import load_dotenv
import os
import requests
import google.generativeai as genai

from auth import verify_api_key
from models import HoneypotRequest, HoneypotResponse
from scam_detector import detect_scam
from session_store import add_message, get_conversation
from intelligence import extract_intelligence

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

app = FastAPI(
    title="Agentic Honeypot API",
    version="1.0.0"
)

@app.get("/")
def health():
    return {
        "status": "running",
        "message": "Agentic Honeypot API with AI is live"
    }

def generate_ai_reply(message: str, conversation: list) -> str:
    prompt = f"""
You are a naive, worried person.
Never say you know this is a scam.
Ask for more details politely.

Conversation:
{conversation}

Latest message:
{message}

Reply shortly.
"""
    try:
        return model.generate_content(prompt).text.strip()
    except Exception:
        return "I am very worried. Can you please explain what I should do next?"

def send_to_guvi(session_id: str, intelligence: dict):
    try:
        requests.post(GUVI_CALLBACK_URL, json={
            "sessionId": session_id,
            "intelligence": intelligence
        }, timeout=5)
    except Exception:
        pass

@app.post("/honeypot", response_model=HoneypotResponse)
def honeypot(
    data: HoneypotRequest = HoneypotRequest(),
    api_key: str = Depends(verify_api_key)
):
    session_id = data.sessionId or "tester-session"
    message = data.message or "Hello"

    add_message(session_id, message)
    conversation = get_conversation(session_id)

    is_scam, _, _ = detect_scam(message)
    intelligence = extract_intelligence(conversation)

    if sum(len(v) for v in intelligence.values()) >= 2:
        send_to_guvi(session_id, intelligence)

    reply = (
        generate_ai_reply(message, conversation)
        if is_scam
        else "Sorry, I didn’t understand. Can you explain again?"
    )

    return {
        "status": "success",
        "reply": reply
    }

