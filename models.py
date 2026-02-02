from pydantic import BaseModel
from typing import Optional

class HoneypotRequest(BaseModel):
    sessionId: str
    message: str

class HoneypotResponse(BaseModel):
    status: str
    reply: str
