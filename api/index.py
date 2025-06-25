from fastapi import APIRouter, Request, HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import resend
import logging
import os
import sqlite3
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

# Piece endpoint
@app.get("/piece/{title}")
async def get_piece(title: str):
    try:
        conn = sqlite3.connect("mydb.sqlite")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.title, c.text AS content, s.title AS style_category, 
                   st.value AS style_value, b.css AS styling, a.name AS auteur
            FROM piece p
            LEFT JOIN content c ON c.piece_id = p.id
            LEFT JOIN style s ON p.style_id = s.id
            LEFT JOIN styles st ON s.id = st.style_id
            LEFT JOIN beauty b ON p.beauty_id = b.id
            LEFT JOIN auteur a ON p.auteur_id = a.id
            WHERE p.title = ? AND p.deleted IS NULL
        """, (title,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Piece not found")

        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "API is running", "endpoints": ["/email/send", "/questions/{id}", "/piece/{title}"]}


from fastapi import APIRouter
import openai
import anthropic
import requests

router = APIRouter()

# ChatGPT Endpoint
@router.post("/chatgpt/")
async def chatgpt(prompt: str):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Claude Endpoint
@router.post("/claude/")
async def claude(prompt: str):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    completion = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.content[0].text

# Grok Endpoint (replace URL with actual API endpoint)
@router.post("/grok/")
async def grok(prompt: str):
    response = requests.post(
        'https://api.grok.example.com/v1/complete',
        headers={"Authorization": f"Bearer {os.getenv('GROK_API_KEY')}"},
        json={"prompt": prompt}
    )
    return response.json()

# Mistral Endpoint (replace URL with actual API endpoint)
@router.post("/mistral/")
async def mistral(prompt: str):
    response = requests.post(
        'https://api.mistral.example.com/v1/complete',
        headers={"Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}"},
        json={"prompt": prompt}
    )
    return response.json()

handler = Mangum(app)
