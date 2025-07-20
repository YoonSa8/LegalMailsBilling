import base64
from bs4 import BeautifulSoup

def decode_base64(data):
    try:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except Exception:
        return ""

def strip_html_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n").strip()

def extract_body_recursive(payload):
    """
    Recursively search for text/plain or fallback to text/html
    """
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    # Prefer text/plain
    if mime_type == "text/plain" and body_data:
        return decode_base64(body_data)

    # Fallback to text/html
    if mime_type == "text/html" and body_data:
        html = decode_base64(body_data)
        return strip_html_tags(html)

    # Recurse into nested parts
    for part in payload.get("parts", []):
        result = extract_body_recursive(part)
        if result:
            return result

    return ""

def parse_email(message):
    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    subject = next((h["value"] for h in headers if h["name"] == "Subject"), None)
    to = next((h["value"] for h in headers if h["name"] == "To"), None)
    from_ = next((h["value"] for h in headers if h["name"] == "From"), None)
    body = extract_body_recursive(payload)

    return {
        "subject": subject,
        "to": to,
        "from": from_,
        "body": body.strip()
    }


