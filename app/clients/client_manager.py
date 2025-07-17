import json
import bcrypt

from app.utils.logging import logger
from app.clients.llm_client import llm_client
from app.clients.redis_client import redis_client
from app.clients.postgre_client import postgre_client
from app.schema.user import Conversation, Chatbot, User

class ClientManager:
    def __init__(self):
        self.llm_client = llm_client
        self.redis_client = redis_client
        self.postgre_client = postgre_client

    def register(self, username: str, password: str) -> User:
        try:
            salt = bcrypt.gensalt()         
            return self.postgre_client.register_user(username, bcrypt.hashpw(password.encode(), salt).decode())
        except ValueError as e:
            raise e

    def login(self, username: str, password: str) -> User:
        user, password_hash = self.postgre_client.get_user_info(username)
        if user and bcrypt.checkpw(password.encode(), password_hash.encode()):
            return user
        return None

    def create_chatbot(self, user_id: str, bot_name: str, prompt: str) -> Chatbot:
        try:
            return self.postgre_client.create_chat_bot(user_id, bot_name, prompt)
        except ValueError as e:
            raise e

    def get_chatbot(self, chatbot_id: str) -> Chatbot:
        try:
            return self.postgre_client.get_chat_bot(chatbot_id)
        except ValueError as e:
            raise e

    def create_conversation(self, user_id: str, bot_id: str, bot_name: str) -> Conversation:
        try:
            return self.postgre_client.create_conversation(user_id, bot_id, bot_name)
        except ValueError as e:
            raise e
        
    def get_conversations(self, user_id: str) -> list[Conversation]:
        return self.postgre_client.get_conversations(user_id)


    async def chat(self, user_id: str, conversation_id: str, prompt: str, message: str, active_conversation: list[dict]) -> str:
        try:
            logger.info(event="chat_request_received",message_length=len(message))

            active_conversation.append({"sender": "User", "message": message})
            response = await self.llm_client.get_response(prompt, active_conversation)

            self.redis_client.append_chat_msg(user_id, conversation_id, json.dumps(active_conversation[-1]))
            active_conversation.append({"sender": "Bot", "message": response})
            self.redis_client.append_chat_msg(user_id, conversation_id, json.dumps(active_conversation[-1]))
            return response
        except Exception as e:
            return e

    def delete_chatbot(self, user_id: str, bot_id: str):
        # self.postgre_client.delete_chat_bot(user_id, bot_id)
        # TODO: Interesting questions whether we would allow user to "actully" delete a chatbot
        # after publish to the community
        raise NotImplementedError("Delete chatbot functionality is not implemented yet.")

    def clear_chat_history(self, user_id: str, conversation_id: str) -> None:
        self.redis_client.clear_chat_history(user_id, conversation_id)

    def get_chat_history(self, user_id: str, conversation_id: str) -> list:
        history = self.redis_client.get_chat_history(user_id, conversation_id)
        return [json.loads(msg) for msg in history] if history else []
        
    
client_manager = ClientManager()
