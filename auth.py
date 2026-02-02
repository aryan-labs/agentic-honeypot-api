from fastapi import Header, HTTPException, status
import os
from dotenv import load_dotenv

load_dotenv()  # <-- THIS WAS MISSING

API_KEY = os.getenv("API_KEY")

def verify_api_key(x_api_key: str = Header(...)):
    if API_KEY is None:
        raise HTTPException(
            status_code=500,
            detail="API_KEY not set in environment"
        )

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
