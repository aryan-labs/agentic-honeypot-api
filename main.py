from fastapi import FastAPI, Depends, Body
from dotenv import load_dotenv
import os
import requests
from typing import Optional

from auth import verify_api_key
from models import HoneypotResponse
from scam_detector import detect_scam
from session_store import add_message, get_conversation
from intelligence import extract_intelligence

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# -------------------------
# Optional AI setup
# -------------------------
ai_enabled = False
model = None

try:
    if GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")
        ai_enabled = True
except Exception:
    ai_enabled = False

# -------------------------
# Initialize FastAPI
# -------------------------
app = FastAPI(
    title="Agentic Honeypot API",
    version="1.0.0"
)

# -------------------------
# Health Check
# -------------------------
@app.get("/")
def health():
    return {
        "status": "running",
        "message": "Agentic Honeypot API is live"
    }

# -------------------------
# AI Reply (SAFE)
# -------------------------
def generate_reply(message: str, conversation: list) -> str:
    # Fallback reply (ALWAYS SAFE)
    fallback = "I am very worried now. Can you please explain what I should do next?"

    if not ai_enabled or not model:
        return fallback

    prompt = f"""
You are a naive, worried person.
Never reveal that you know this is a scam.
Ask politely for more details.

Conversation:
{conversation}

Latest message:
{message}

Reply shortly.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else fallback
    except Exception:
        return fallback

# -------------------------
# GUVI Callback (SAFE)
# -------------------------
def send_to_guvi(session_id: str, intelligence: dict):
    if not GUVI_CALLBACK_URL:
        return
    try:
        requests.post(
            GUVI_CALLBACK_URL,
            json={
                "sessionId": session_id,
                "intelligence": intelligence
            },
            timeout=3
        )
    except Exception:
        pass

# -------------------------
# MAIN ENDPOINT (BULLETPROOF)
# -------------------------
@app.post("/honeypot", response_model=HoneypotResponse)
def honeypot(
    data: Optional[dict] = Body(None),
    api_key: str = Depends(verify_api_key)
):
    session_id = "tester-session"
    message = "Hello"

    if data:
        session_id = data.get("sessionId", session_id)
        message = data.get("message", message)

    add_message(session_id, message)
    conversation = get_conversation(session_id)

    is_scam, _, _ = detect_scam(message)
    intelligence = extract_intelligence(conversation)

    if sum(len(v) for v in intelligence.values()) >= 2:
        send_to_guvi(session_id, intelligence)

    reply = (
        generate_reply(message, conversation)
        if is_scam
        else "Sorry, I didn’t understand. Can you explain again?"
    )

    return {
        "status": "success",
        "reply": reply
    }

