from fastapi import APIRouter, Request, HTTPException
import resend, os

router = APIRouter(prefix="/email")

resend.api_key = os.getenv("RESEND_API_KEY")

@router.post("/send")
async def send_email(request: Request):
    data = await request.json()
    try:
        resend.Emails.send({
            "from": os.getenv("RESEND_FROM_EMAIL"),
            "to": os.getenv("RESEND_FROM_EMAIL"),
            "subject": data["subject"],
            "text": f"{data['name']} ({data['email']}): {data['message']}"
        })
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
