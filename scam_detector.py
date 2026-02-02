import re

SCAM_KEYWORDS = {
    "urgency": ["urgent", "immediately", "now", "today", "asap", "verify"],
    "threat": ["blocked", "suspended", "deactivated", "legal action"],
    "bank": ["bank", "account", "kyc", "ifsc", "upi", "atm"],
    "payment": ["pay", "payment", "transfer", "send", "upi"],
    "prize": ["winner", "lottery", "prize", "reward"]
}

def detect_scam(message: str):
    message_lower = message.lower()
    matched = []

    for category, words in SCAM_KEYWORDS.items():
        for word in words:
            if re.search(rf"\b{word}\b", message_lower):
                matched.append(word)
                break

    score = len(matched)
    is_scam = score >= 2
    confidence = min(score / 5, 1.0)

    return is_scam, round(confidence, 2), matched
