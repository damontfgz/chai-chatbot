import gradio as gr
import json

from dataclasses import dataclass, field
from app.clients.client_manager import client_manager
from app.clients.prompts import DEFAULT_FALLBACK_REPLY
from app.utils.logging import logger
from app.schema.user import Chatbot


# Isolating user state per each logged-in user
# This is a simple state management for demo purposes with Gradio.
@dataclass
class UserState:
    user_id: int = None
    username: str = None
    past_conversations: list = field(default_factory=list)
    active_conversation: list = field(default_factory=list)
    active_chatbot: Chatbot = None

def parse_chat_history(chat_history):
    def parse(msg):
        if msg["sender"].lower() == "user":
            role = "user"
        else:
            role = "assistant"
        return {
            "role": role,
            "content": msg["message"]
        }
    return [parse(c) for c in chat_history]


def login(username, password, user_state):
    login_user = client_manager.login(username, password)
    if login_user:
        user_state.user_id = login_user.id  
        user_state.username = login_user.name
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), user_state, None
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), user_state, "Username or password is incorrect. Please try again."


def register(username, password, user_state):
    try:
        register_user = client_manager.register(username, password)
        user_state.user_id = register_user.id
        user_state.username = register_user.name
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), user_state, None
    except ValueError as e:
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), user_state, f"Registration failed: {str(e)}"
    

def create_chatbot(chatbot_name, chatbot_prompt, user_state):
    chatbot = client_manager.create_chatbot(user_state.user_id, chatbot_name, chatbot_prompt)
    conversation = client_manager.create_conversation(user_state.user_id, chatbot.id, chatbot.name)
    user_state.past_conversations.append(conversation)
    return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), user_state, \
           gr.update(label="Chatbot Name", placeholder="Enter a name for your chatbot"), \
           gr.update(label="Chatbot Prompt", placeholder="Enter a prompt for your chatbot")

def get_past_conversations(user_state):
    past_conversations = client_manager.get_conversations(user_state.user_id)
    if past_conversations:
        user_state.past_conversations = past_conversations
        return gr.update(value=f"Chat with {past_conversations[-1].chatbot_name}", visible=True), None

    return gr.update(visible=False), "No past conversations found." 

def get_chat_history(user_state):
    if user_state.past_conversations:
        chat_history = client_manager.get_chat_history(user_state.user_id, user_state.past_conversations[-1].id)
        chat_bot = client_manager.get_chatbot(user_state.past_conversations[-1].chatbot_id)
        user_state.active_chatbot = chat_bot
        user_state.active_conversation = chat_history
        return gr.Textbox(value=chat_bot.prompt, label=f"Prompt for {chat_bot.name}"), parse_chat_history(chat_history), user_state
    return None, []

def on_clear(user_state):
    client_manager.clear_chat_history(user_state.user_id, user_state.past_conversations[-1].id)
    return []



def create_gradio_ui():
    with gr.Blocks(theme="soft") as ui:

        user_state = gr.State(UserState())  

        with gr.Column() as login_page:
            gr.Markdown("# Welcome to CHAI Chat")
            gr.Markdown("Please enter your username to start using our services")

            username = gr.Textbox(label="Username", placeholder="Enter your username")
            password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")

            login_button = gr.Button("Login")
            login_status = gr.Markdown()
            register_button = gr.Button("New User? Register!")
            register_status = gr.Markdown()

        
        with gr.Column() as user_page:
            gr.Markdown("# CHAI Chat")
            
            gr.Markdown("## Your Last Conversation")
            prev_chat = gr.Button(visible=False)
            prev_chat_status = gr.Markdown()

            gr.Markdown("## Create your personalized Chatbot")
            chatbot_name = gr.Textbox(label="Chatbot Name", placeholder="Enter a name for your chatbot")
            chatbot_prompt = gr.Textbox(label="Chatbot Prompt", placeholder="Enter a prompt for your chatbot")
            create_chatbot_button = gr.Button("Create Chatbot")

            # gr.Markdown("You can chat with the popular bots below")
            # list of chatbots created by other users


        with gr.Column() as chat_page:

            system_prompt_display = gr.Textbox()

            chatbot = gr.Chatbot(type="messages", elem_classes=["small-font"])
            msg = gr.Textbox(elem_classes=["small-font"])
            clear = gr.ClearButton(value="Clear Chat History", inputs=[msg, chatbot])
            return_button = gr.Button("Return to home page")

            async def respond(message, gradio_chat_history, user_state):
                try:
                    user_id = user_state.user_id
                    active_conversation_id = user_state.past_conversations[-1].id
                    active_conversation = user_state.active_conversation
                    active_chatbot = user_state.active_chatbot

                    gradio_chat_history.append({"role": "user", "content": message})
                    response = await client_manager.chat(user_id, active_conversation_id, active_chatbot.prompt, message, active_conversation)
                    user_state.active_conversation = active_conversation
                    gradio_chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    # In case of failure where model endpoint is not returning result, return
                    # fallback info for better user experience
                    logger.exception(event="fallback_reply_applied", extra={"exception": str(e)})
                    gradio_chat_history.append({"role": "assistant", "content": DEFAULT_FALLBACK_REPLY})
                return "", gradio_chat_history, user_state


        login_button.click(
            login,
            inputs=[username, password, user_state],
            outputs=[login_page, user_page, chat_page, user_state, login_status]
        ).then(
            get_past_conversations,
            inputs=[user_state],
            outputs=[prev_chat, prev_chat_status]
        )

        register_button.click(
            register,
            inputs=[username, password, user_state],
            outputs=[login_page, user_page, chat_page,user_state, register_status]
        ).then(
            get_past_conversations,
            inputs=[user_state],
            outputs=[prev_chat, prev_chat_status]
        )

        create_chatbot_button.click(
            create_chatbot,
            inputs=[chatbot_name, chatbot_prompt, user_state],
            outputs=[login_page, user_page, chat_page, user_state]
        ).then(
            get_chat_history,
            inputs=[user_state],
            outputs=[system_prompt_display, chatbot, user_state]
        )

        prev_chat.click(
            lambda: (gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)),
            inputs=[],
            outputs=[login_page, user_page, chat_page]
        ).then(
            get_chat_history,
            inputs=[user_state],
            outputs=[system_prompt_display, chatbot, user_state]
        )

        msg.submit(respond, inputs=[msg, chatbot, user_state], outputs=[msg, chatbot, user_state])
        clear.click(on_clear, inputs=[user_state], outputs=[chatbot], queue=False)

        return_button.click(
            lambda: (gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)),
            inputs=[],
            outputs=[login_page, user_page, chat_page]
        ).then(
            get_past_conversations,
            inputs=[user_state],
            outputs=[prev_chat, prev_chat_status]
        )

        login_page.visible = True
        user_page.visible = False
        chat_page.visible = False

    return ui