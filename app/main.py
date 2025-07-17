from fastapi import FastAPI
from gradio.routes import mount_gradio_app
from app.gradio_ui import create_gradio_ui
from app.services.api import api_router
from contextlib import asynccontextmanager
from app.clients.llm_client import llm_client
from app.utils.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(event="application_startup")
    yield
    await llm_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
app = mount_gradio_app(app, create_gradio_ui(), path="/chatbot")