from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.openai_service import handle_retrieval_query, handle_direct_openai_query

router = APIRouter()

class QueryModel(BaseModel):
    query: str

@router.post("/query")
async def handle_query(query_model: QueryModel, from_context: bool = Query(False)):
    try:
        if from_context:
            # Use retrieval-based query
            answer = handle_retrieval_query(query_model.query)
        else:
            # Use direct OpenAI-based query
            answer = handle_direct_openai_query(query_model.query)
        return {"query": query_model.query, "answer": answer}
    except RuntimeError as e:
        # Handle errors in processing queries
        raise HTTPException(status_code=500, detail=str(e))
