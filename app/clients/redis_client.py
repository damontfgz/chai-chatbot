import valkey
from app.config.settings import REDIS_URL, REDIS_PORT


class RedisClient:

    def __init__(self, redis_url=REDIS_URL, port=REDIS_PORT):
        self.client = valkey.Valkey(host=redis_url, port=port, db=0)

    def append_chat_msg(self, user_id: str, conversation_id, msg: str):
        self.client.rpush(f"{user_id}:{conversation_id}", msg)

    def get_chat_history(self, user_id: str, conversation_id, range=-1):
        return self.client.lrange(f"{user_id}:{conversation_id}", 0, range)
    
    def clear_chat_history(self, user_id: str, conversation_id):
        self.client.delete(f"{user_id}:{conversation_id}")

redis_client = RedisClient()

