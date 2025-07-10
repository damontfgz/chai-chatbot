import httpx

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.clients.llm_client import get_llm_client
from pydantic import BaseModel
from app.utils.logging import logger

llm_client = get_llm_client()

class ChatRequest(BaseModel):
    content: str

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.content or len(request.content) == 0:
        return JSONResponse(
            status_code=400,
            content={"error": "Input cannot be empty"}
        )

    try:
        response = await llm_client.get_response(request.content)
        return JSONResponse(
            status_code=200,
            content={"content": response}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )







