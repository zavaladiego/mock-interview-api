from typing import Dict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.openai_service import InterviewSession, handle_retrieval_query

router = APIRouter()

# Dictionary to store user sessions
user_sessions: Dict[str, InterviewSession] = {}

class QueryModel(BaseModel):
    query: str
    user_id: int

@router.post("/query")
async def handle_query(new_session: bool, query_model: QueryModel, from_context: bool = Query(False)):
    try:
        user_id = query_model.user_id

        if new_session or user_id not in user_sessions:
            # Create a new session for the user
            user_sessions[user_id] = InterviewSession()

        session = user_sessions[user_id]

        if from_context:
            # Use retrieval-based query
            answer = handle_retrieval_query(query_model.query)
        else:
            # Use direct OpenAI-based query
            answer = session.handle_direct_openai_query(query_model.query)

        return {"query": query_model.query, "answer": answer}
    except RuntimeError as e:
        # Handle errors in processing queries
        raise HTTPException(status_code=500, detail=str(e))
