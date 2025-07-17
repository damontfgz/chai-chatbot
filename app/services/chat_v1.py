from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.clients.llm_client import llm_client
from pydantic import BaseModel
from google import genai
from google.genai.types import HttpOptions

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

client = genai.Client(http_options=HttpOptions(api_version="v1"))

@router.post("/chat/vertexai")
async def chat_vertex(request: ChatRequest):
    async def generate_content(prompt: str):
        response =  client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=prompt
        )
        return response.text

    return JSONResponse(
            status_code=200,
            content={"content": await generate_content(request.content)}
        )





