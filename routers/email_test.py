from fastapi import APIRouter, HTTPException
import resend
import os

router = APIRouter()

resend.api_key = os.getenv("RESEND_API_KEY")

if not resend.api_key:
    raise RuntimeError("RESEND_API_KEY is not set in your environment")

@router.get("/test-email/")
async def send_test_email(to_email: str):
    try:
        response = resend.Emails.send({
            "from": "stevie@rainharder.com",  # Replace explicitly
            "to": [to_email],
            "subject": "Test Email from FastAPI",
            "text": "This is a test email sent from FastAPI via Resend.",
        })
        return {"message": "Email sent successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))