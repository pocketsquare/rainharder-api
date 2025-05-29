from fastapi import APIRouter, HTTPException
from database import database

router = APIRouter()

@router.get("/questions/{question_id}")
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
