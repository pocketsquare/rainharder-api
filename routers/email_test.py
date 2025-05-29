from fastapi import APIRouter, HTTPException
from services.email import send_email

router = APIRouter()

@router.get("/test-email/")
async def test_email(to_email: str):
    subject = "Rainharder Email Test"
    html_content = "<strong>This is a test email from Rainharder API via Resend.</strong>"
    try:
        response = await send_email(to_email, subject, html_content)
        return {"status": "sent", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))