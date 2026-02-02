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

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

API_KEY = os.getenv("API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL")

# -------------------------
# Configure Gemini
# -------------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# -------------------------
# Initialize FastAPI
# -------------------------
app = FastAPI(
    title="Agentic Honeypot API",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)

# -------------------------
# Health Check
# -------------------------
@app.get("/")
def health_check():
    return {
        "status": "running",
        "message": "Agentic Honeypot API with AI is live"
    }

# -------------------------
# Helper: Generate AI Reply
# -------------------------
def generate_ai_reply(message: str, conversation: list) -> str:
    history = "\n".join(conversation[-5:])

    prompt = f"""
You are pretending to be a naive, elderly, non-technical person.
You believe the scammer and are worried.
You must NEVER reveal that you know this is a scam.
You must ask questions to get more details like bank account, UPI, phone number, or link.

Conversation so far:
{history}

Latest message:
{message}

Reply in 1–2 short, natural sentences.
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "I am very worried now. Can you please explain what I should do next?"

# -------------------------
# Helper: Send data to GUVI
# -------------------------
def send_to_guvi(session_id: str, intelligence: dict):
    payload = {
        "sessionId": session_id,
        "intelligence": intelligence
    }

    try:
        requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
    except Exception:
        pass  # Do not crash system

# -------------------------
# Main Honeypot Endpoint
# -------------------------
@app.post("/honeypot", response_model=HoneypotResponse)
def honeypot_endpoint(
    data: HoneypotRequest,
    api_key: str = Depends(verify_api_key)
):
    # 1. Store message
    add_message(data.sessionId, data.message)

    # 2. Get conversation
    conversation = get_conversation(data.sessionId)

    # 3. Detect scam
    is_scam, confidence, matched_keywords = detect_scam(data.message)

    # 4. Extract intelligence
    intelligence = extract_intelligence(conversation)

    # 5. Decide if we should send final callback
    total_intel = sum(len(v) for v in intelligence.values())
    if total_intel >= 2:
        send_to_guvi(data.sessionId, intelligence)

    # 6. Generate reply
    if is_scam:
        reply_text = generate_ai_reply(data.message, conversation)
    else:
        reply_text = "Sorry, I am not understanding this properly. Can you explain again?"

    return {
        "status": "success",
        "reply": reply_text
    }
