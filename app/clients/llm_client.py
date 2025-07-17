import httpx

from app.utils.logging import logger
from app.clients.prompts import DEFAULT_SAFETY_PROMPT
from app.config.settings import MODEL_SERVING_ENDPOINT, API_TOKEN
from pydantic import BaseModel
from google import genai
from google.genai.types import HttpOptions


class LLMRequest(BaseModel):
    # TODO: Some clarification could help to further optimize the implementation
    # - if conversation history will be truncated, where should this be happened at the api layer or modeling serving side
    # - what is the relation the bot/user_name vs "role" inside chat_history
    # - is chat_history expecting conversation happened in some specific order? user/bot/user ... How about usre/user/bot...
    memory: str = ""
    prompt: str
    bot_name: str = "Bot"
    user_name: str = "User"
    chat_history: list

class LLMClient:

    def __init__(self, endpoint=MODEL_SERVING_ENDPOINT, token=API_TOKEN):
        self.endpoint = endpoint
        self.token = token
        self.client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            timeout=10.0)
        # self.client = genai.Client(http_options=HttpOptions(api_version="v1"))
        logger.info(event="llm_client_initialized", endpoint=endpoint)

    async def get_response(self, prompt: str, active_conversation: list) -> str:

        payload = LLMRequest(
            prompt=f"{DEFAULT_SAFETY_PROMPT} {prompt}",
            chat_history=active_conversation
        ).model_dump()
        try:
            response = await self.client.post(
                url=self.endpoint,
                json=payload
            )
            # response = self.client.models.generate_content(
            #     model="gemini-2.0-flash-001",
            #     contents=message
            # )
            # return response.text

            response.raise_for_status()
            data = response.json()

            if "model_output" not in data:
                logger.error(event="model_output_missing", extra={"response": data})
                raise ValueError("LLM response missing 'model_output'")

            return data["model_output"]
        except httpx.HTTPStatusError as e:
            logger.error(event="llm_model_request_failed", extra={"exception": str(e)})
            raise e
        # any other exceptions need to be observed should be caught as well

    async def close(self):
        await self.client.aclose()

# TODO: use fastAPI native depedency injection for sharing different clients
llm_client = LLMClient()