import httpx

from app.utils.logging import logger
from app.clients.prompts import DEFAULT_SAFETY_PROMPT
from app.config.settings import MODEL_SERVING_ENDPOINT, API_TOKEN
from pydantic import BaseModel


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
        # For now implementation only support single user, next improvements will be
        # - support userid generation and session management, so that chat and prompt are managed separately
        # - store chat msg so that history is maintained persistently

        self.endpoint = endpoint
        self.token = token
        self.client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            timeout=10.0)
        self.chat_history = []
        self.prompt = DEFAULT_SAFETY_PROMPT
        logger.info(event="llm_client_initialized", endpoint=endpoint)

    async def get_response(self, message: str) -> str:
        logger.info(event="chat_request_received",message_length=len(message))

        self.chat_history.append({"sender": "User", "message": message})
        payload = LLMRequest(
            prompt=self.prompt,
            chat_history=self.chat_history
        ).model_dump()
        try:
            response = await self.client.post(
                url=self.endpoint,
                json=payload
            )
            response.raise_for_status()

            data = response.json()

            if "model_output" not in data:
                logger.error(event="model_output_missing", extra={"response": data})
                raise ValueError("LLM response missing 'model_output'")

            self.chat_history.append({"sender": "Bot", "message": data["model_output"]})
            return data["model_output"]
        except httpx.HTTPStatusError as e:
            logger.error(event="llm_model_request_failed", extra={"exception": str(e)})
            raise e
        # any other exceptions need to be observed should be caught as well

    def configure_prompt(self, prompt: str):
        # TODO: the provided prompts does not seem to be very effective, some further investigation needed
        self.prompt += prompt

    def clear_chat_history(self):
        self.chat_history.clear()
        self.prompt = DEFAULT_SAFETY_PROMPT
        logger.info(event="chat_history_cleared")

    async def close(self):
        await self.client.aclose()

# TODO: use fastAPI native depedency injection for sharing different clients
llm_client = LLMClient()
def get_llm_client():
    return llm_client