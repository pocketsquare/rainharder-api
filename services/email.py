import os
from resend import Resend

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")

resend = Resend(api_key=RESEND_API_KEY)

async def send_email(to_email: str, subject: str, html_content: str):
    params = {
        "from": RESEND_FROM_EMAIL,
        "to": to_email,
        "subject": subject,
        "html": html_content,
    }
    response = resend.emails.send(params)
    return response
