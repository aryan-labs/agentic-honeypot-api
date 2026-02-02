import re
from typing import Dict, List

PHONE_REGEX = r"(?:\+91[-\s]?)?[6-9]\d{9}"
UPI_REGEX = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
URL_REGEX = r"https?://[^\s]+"

def extract_intelligence(messages: List[str]) -> Dict[str, List[str]]:
    """
    Extract intelligence from conversation messages
    """

    full_text = " ".join(messages)

    phones = list(set(re.findall(PHONE_REGEX, full_text)))
    upis = list(set(re.findall(UPI_REGEX, full_text)))
    urls = list(set(re.findall(URL_REGEX, full_text)))

    return {
        "phone_numbers": phones,
        "upi_ids": upis,
        "phishing_links": urls
    }
