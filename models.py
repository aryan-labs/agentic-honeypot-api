from pydantic import BaseModel
from typing import Optional

class HoneypotRequest(BaseModel):
    sessionId: Optional[str] = "tester-session"
    message: Optional[str] = "Hello"

class HoneypotResponse(BaseModel):
    status: str
    reply: str
