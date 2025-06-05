from fastapi import APIRouter, Request, HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import resend
import logging
import os
from mangum import Mangum
from dotenv import load_dotenv
from database import database

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS first
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,https://rainharder.com,https://www.rainharder.com").split(",")
logger.debug(f"Allowed CORS origins: {origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email endpoint
@app.post("/email/send")
async def send_email(request: Request):
    try:
        resend_api_key = os.getenv("RESEND_API_KEY")
        if not resend_api_key:
            logger.error("RESEND_API_KEY environment variable is not set")
            raise RuntimeError("RESEND_API_KEY environment variable is not set")

        resend.api_key = resend_api_key

        data = await request.json()
        logger.debug(f"Received data: {data}")
        name = data.get("name", "")
        email = data.get("email", "")
        subject = data.get("subject", "")
        message = data.get("message", "")

        if not name or not email or not subject or not message:
            raise HTTPException(status_code=400, detail="All fields required.")

        params = {
            "from": "stevie@rainharder.com",
            "to": ["stevie@rainharder.com"],
            "reply_to": email,
            "subject": subject,
            "text": f"Name: {name}\nEmail: {email}\nMessage: {message}"
        }
        logger.debug(f"Sending email with params: {params}")
        response = resend.Emails.send(params)
        logger.debug(f"Resend response: {response}")
        return {"status": "sent"}

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Questions endpoint
@app.get("/questions/{question_id}")
async def get_question(question_id: int):
    query = "SELECT * FROM questions WHERE id = :id"
    question = await database.fetch_one(query, {"id": question_id})
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    left_entries_query = "SELECT * FROM left_entries WHERE question_id = :question_id"
    right_entries_query = "SELECT * FROM right_entries WHERE question_id = :question_id"

    left_entries = await database.fetch_all(left_entries_query, {"question_id": question_id})
    right_entries = await database.fetch_all(right_entries_query, {"question_id": question_id})

    return {
        "id": question["id"],
        "prompt": question["prompt"],
        "left_entries": [dict(le) for le in left_entries],
        "right_entries": [dict(re) for re in right_entries],
    }

handler = Mangum(app)