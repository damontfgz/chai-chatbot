from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    name: str

@dataclass
class Chatbot:
    id: int
    name: str
    owner_id: int
    prompt: str

@dataclass
class Conversation:
    id: int
    user_id: int
    chatbot_id: int
    chatbot_name: str
