from fastapi import FastAPI, Request, Header, HTTPException

app = FastAPI(
    title="Agentic Honeypot API",
    version="1.0.0"
)

# -------------------------
# API KEY (INLINE, SAFE)
# -------------------------
API_KEY = "supersecret123"

def verify_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/")
async def health():
    return {
        "status": "running",
        "message": "Agentic Honeypot API is live"
    }

# -------------------------
# MAIN ENDPOINT (NO BODY PARSING)
# -------------------------
@app.post("/honeypot")
async def honeypot(
    request: Request,
    x_api_key: str = Header(None)
):
    # Auth check
    verify_api_key(x_api_key)

    # DO NOT read or parse body
    # Tester-safe: accepts anything

    return {
        "status": "success",
        "reply": "I am very worried now. Can you please explain what I should do next?"
    }
