from contextlib import asynccontextmanager
import functools

import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware


from app.services.ocr_text.surya.detection import DetectionPredictor
from app.services.ocr_text.surya.recognition import RecognitionPredictor
from app.services.ocr_text.surya.layout import LayoutPredictor
from app.services.ocr_text.surya.table_rec import TableRecPredictor
from app.api.api_router import router
from app.common.config import settings

from app.helpers.exception_handler import (
    BaseHTTPException,
    CustomException,
    base_exception_handler,
    custom_404_handler,
    custom_validation_error,
    http_exception_handler,
)
import os
import logging

connection = None
logger = logging.getLogger("__name__")

os.environ["TOKENIZERS_PARALLELISM"] = "false"
origins = [
    "*",
    "http://localhost:8080"
]

@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.db = app.database

    app.state.models = load_models()
    # consumer_task = asyncio.create_task(kafka_consumer.consume_messages(app.state.db))

    yield
    app.client.close()


def load_models():
    logger.info("Loading OCR models...")
    return {
        "det": DetectionPredictor(),
        "rec": RecognitionPredictor(),
        "table": TableRecPredictor(),
        "layout": LayoutPredictor(),
    }

def get_application(app_config: dict) -> FastAPI:
    application = FastAPI(**app_config)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix=settings.API_PREFIX)
    application.add_exception_handler(BaseHTTPException, base_exception_handler)
    application.add_exception_handler(CustomException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, custom_validation_error)
    application.add_exception_handler(404, custom_404_handler)
    return application


app_config = {
    "title": f"{settings.PROJECT_NAME}",
    "docs_url": "/docs",
    "redoc_url": "/re-docs",
    "openapi_url": f"{settings.API_PREFIX}/openapi.json",
    "description": "Chatbot Management System",
    "lifespan": lifespan,
}
app = get_application(app_config)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

