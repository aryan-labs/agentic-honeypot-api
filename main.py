from fastapi import FastAPI, Depends, Body
from dotenv import load_dotenv
import os
import requests
import google.generativeai as genai
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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

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
        "message": "Agentic Honeypot API with AI is live"
    }

# -------------------------
# AI Reply Generator
# -------------------------
def generate_ai_reply(message: str, conversation: list) -> str:
    prompt = f"""
You are a naive, worried person.
You must never reveal that you know this is a scam.
Ask politely for more details like account, UPI, phone, or link.

Conversation:
{conversation}

Latest message:
{message}

Reply shortly and naturally.
"""
    try:
        return model.generate_content(prompt).text.strip()
    except Exception:
        return "I am really worried. Can you please tell me what I should do next?"

# -------------------------
# Send Callback to GUVI
# -------------------------
def send_to_guvi(session_id: str, intelligence: dict):
    try:
        requests.post(
            GUVI_CALLBACK_URL,
            json={
                "sessionId": session_id,
                "intelligence": intelligence
            },
            timeout=5
        )
    except Exception:
        pass  # Never crash the API

# -------------------------
# MAIN ENDPOINT (FINAL FIX)
# -------------------------
@app.post("/honeypot", response_model=HoneypotResponse)
def honeypot(
    data: Optional[dict] = Body(None),   # 👈 THIS IS THE KEY FIX
    api_key: str = Depends(verify_api_key)
):
    # Handle missing body (tester case)
    session_id = "tester-session"
    message = "Hello"

    if data:
        session_id = data.get("sessionId", session_id)
        message = data.get("message", message)

    # Store conversation
    add_message(session_id, message)
    conversation = get_conversation(session_id)

    # Detect scam
    is_scam, _, _ = detect_scam(message)

    # Extract intelligence
    intelligence = extract_intelligence(conversation)

    # Send callback if enough intel
    if sum(len(v) for v in intelligence.values()) >= 2:
        send_to_guvi(session_id, intelligence)

    # Generate reply
    reply = (
        generate_ai_reply(message, conversation)
        if is_scam
        else "Sorry, I didn’t understand. Can you explain again?"
    )

    return {
        "status": "success",
        "reply": reply
    }
