from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import email
from dotenv import load_dotenv
import sqlite3
import os

# Load the .env file
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://rainharder.com"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email.router)

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