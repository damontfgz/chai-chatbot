import psycopg

from app.schema.user import Chatbot, User, Conversation

class PostgreClient:
    def __init__(self, db_name="postgres", user="postgres", password="admin", host='localhost', port=5432):
        self.connection = psycopg.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def register_user(self, username: str, password_hash: str) -> User:
        self.cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            RETURNING user_id, username;
            """,
            (username, password_hash)
        )
        try:
            user_id, username = self.cursor.fetchone()
            self.connection.commit()
            return User(id=user_id, name=username)
        except psycopg.errors.UniqueViolation:
            self.connection.rollback()
            raise ValueError(f"Username already exists: {username}")
        except psycopg.Error as e:
            self.connection.rollback()
            raise ValueError(f"Failed to register user: {e}")

    def verify_user_login(self, username: str, password_hash: str) -> User:
        self.cursor.execute(
            """
            SELECT user_id, username, created_at FROM users
            WHERE username = %s AND password_hash = %s;
            """,
            (username, password_hash)
        )
        user = self.cursor.fetchone()
        if user:
            return User(id=user[0], name=user[1])
        return None

    def create_chat_bot(self, user_id: str, bot_name: str, prompt: str) -> Chatbot:
        self.cursor.execute(
            """
            INSERT INTO chatbots (owner_id, name, prompt)
            VALUES (%s, %s, %s)
            RETURNING bot_id, name, prompt;
            """,
            (user_id, bot_name, prompt)
        )
        try:
            bot = self.cursor.fetchone()
            self.connection.commit()
            return Chatbot(id=bot[0], name=bot[1], owner_id=user_id, prompt=bot[2])
        except psycopg.Error as e:
            self.connection.rollback()
            raise ValueError(f"Failed to create chat bot: {e}")

    def get_chat_bot(self, bot_id: str) -> Chatbot:
        self.cursor.execute(
            """
            SELECT bot_id, name, owner_id, prompt FROM chatbots
            WHERE bot_id = %s;
            """,
            (bot_id,)
        )
        bot = self.cursor.fetchone()
        if bot:
            return Chatbot(id=bot[0], name=bot[1], owner_id=bot[2], prompt=bot[3])
        return None

    def create_conversation(self, user_id: str, bot_id: str, bot_name: str) -> Conversation:
        self.cursor.execute(
            """
            INSERT INTO conversations (user_id, bot_id)
            VALUES (%s, %s)
            RETURNING conversation_id;
            """,
            (user_id, bot_id)
        )
        try:
            conversation = self.cursor.fetchone()
            self.connection.commit()
            return Conversation(id=conversation[0], user_id=user_id, chatbot_id=bot_id, chatbot_name=bot_name)
        except psycopg.Error as e:
            self.connection.rollback()
            raise ValueError(f"Failed to create conversation: {e}")
        

    def get_conversations(self, user_id: str) -> list[Conversation]:
        self.cursor.execute(
            """
            SELECT
                c.conversation_id,
                c.bot_id,
                u.username,
                b.name AS bot_name
            FROM
                conversations c
            INNER JOIN users u ON c.user_id = u.user_id
            INNER JOIN chatbots b ON c.bot_id = b.bot_id
            WHERE
                c.user_id = %s
            ORDER BY
                c.created_at ASC;
            """,
            (user_id,)
        )
        conversations = self.cursor.fetchall()
        return [Conversation(id=conv[0], user_id=user_id, chatbot_id=conv[1], chatbot_name=conv[3]) for conv in conversations]
    
postgre_client = PostgreClient()