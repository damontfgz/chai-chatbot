import gradio as gr

from app.clients.llm_client import get_llm_client
from app.clients.prompts import DEFAULT_FALLBACK_REPLY
from app.utils.logging import logger

llm_client = get_llm_client()

def create_gradio_ui():
    with gr.Blocks(theme="soft") as ui:

        chatbot = gr.Chatbot(type="messages", elem_classes=["small-font"])
        msg = gr.Textbox(elem_classes=["small-font"])
        clear = gr.ClearButton([msg, chatbot])

        async def respond(message, chat_history):
            try:
                chat_history.append({"role": "user", "content": message})
                response = await llm_client.get_response(message)
                chat_history.append({"role": "assistant", "content": response})
            except Exception as e:
                logger.exception(event="fallback_reply_applied", extra={"exception": str(e)})
                chat_history.append({"role": "assistant", "content": DEFAULT_FALLBACK_REPLY})
            return "", chat_history

        def on_clear():
            llm_client.clear_chat_history()
            return []

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(fn=lambda: on_clear(), inputs=None, outputs=chatbot, queue=False)
    return ui