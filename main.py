from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import email
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://rainharder.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email.router)