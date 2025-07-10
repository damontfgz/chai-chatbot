from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.clients.llm_client import get_llm_client
from pydantic import BaseModel

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
        # we should be replying different status code per the type of exception caught, but
        # since we are not doing much validation for the demo, this part is left for further improvement
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )







