import gradio as gr

from app.clients.llm_client import get_llm_client
from app.clients.prompts import DEFAULT_FALLBACK_REPLY
from app.utils.logging import logger

llm_client = get_llm_client()

def create_gradio_ui():
    with gr.Blocks(theme="soft") as ui:

        system_prompt_input = gr.Textbox(
            label="Custom Prompt For Chatbot",
            placeholder="e.g. You are a helpful assistant.",
        )
        system_prompt_display = gr.Textbox(
            label="Active Prompt",
            interactive=False,
            visible=False,
        )

        chatbot = gr.Chatbot(type="messages", elem_classes=["small-font"])
        msg = gr.Textbox(elem_classes=["small-font"])
        clear = gr.ClearButton(value="Clear Chat History", inputs=[msg, chatbot, system_prompt_input, system_prompt_display])

        def set_system_prompt(prompt: str):
            llm_client.configure_prompt(prompt)
            return (
                gr.update(value=prompt, visible=True),
                gr.update(visible=False)
            )

        async def respond(message, chat_history):
            try:
                chat_history.append({"role": "user", "content": message})
                response = await llm_client.get_response(message)
                chat_history.append({"role": "assistant", "content": response})
            except Exception as e:
                # In case of failure where model endpoint is not returning result, return
                # fallback info for better user experience
                logger.exception(event="fallback_reply_applied", extra={"exception": str(e)})
                chat_history.append({"role": "assistant", "content": DEFAULT_FALLBACK_REPLY})
            return "", chat_history

        def on_clear():
            llm_client.clear_chat_history()
            return [], gr.update(value="", visible=True), gr.update(value="", visible=False)

        system_prompt_input.submit(
            fn=set_system_prompt,
            inputs=system_prompt_input,
            outputs=[system_prompt_display, system_prompt_input]
        )

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(fn=lambda: on_clear(), inputs=None, outputs=[chatbot, system_prompt_input, system_prompt_display], queue=False)
    return ui