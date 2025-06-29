from contextlib import asynccontextmanager

import uvicorn
import asyncio
from app.messaging import kafka_consumer
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware

from app.services.ocr_text.surya.model.detection.segformer import load_model as load_detection_model, load_processor as load_detection_processor
from app.services.ocr_text.surya.model.recognition.model import load_model as load_recognition_model
from model.recognition.processor import load_processor as load_recognition_processor
from paddleocr import PaddleOCR
from app.services.recognition_service.vietocr.tool.predictor import Predictor
from app.services.recognition_service.vietocr.tool.config import Cfg

from app.api.api_router import router
from app.common.config import settings
from app.db.base import init_db
from app.helpers.exception_handler import (
    BaseHTTPException,
    CustomException,
    base_exception_handler,
    custom_404_handler,
    custom_validation_error,
    http_exception_handler,
)

origins = [
    "*",
    "http://localhost:8080"
]

config = Cfg.load_config_from_name_local(settings.DIR_BASE_YML, settings.DIR_MODEL_YML)
config['cnn']['pretrained']=False
config['device'] = 'cuda'
print(f"config.........{config}")
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(app)

    app.state.db = app.database

    det_processor = load_detection_processor()
    det_model = load_detection_model()
    rec_model = load_recognition_model()
    rec_processor = load_recognition_processor()
    paddelocr = PaddleOCR(lang=settings.LANG_PPOCR ,rec_algorithm=settings.REC_ALGORITHM, use_gpu=settings.MODEL_DEVICE)
    model_vietocr = Predictor(config)
    # Start Kafka consumer
    consumer_task = asyncio.create_task(kafka_consumer.consume_messages(app.state.db, det_processor, det_model))
    consumer_task_recog = asyncio.create_task(kafka_consumer.consume_messages_recog(app.state.db, det_processor, det_model, rec_processor, rec_model, paddelocr, model_vietocr))

    yield


    # Close Kafka consumer when app shuts down
    consumer_task.cancel()
    consumer_task_recog.cancel()
    try:
        await consumer_task
        await consumer_task_recog
    except asyncio.CancelledError:
        print(f"Cancel consumer")
        pass

    app.client.close()


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
    "description": "OCR Management System",
    "lifespan": lifespan,
}
app = get_application(app_config)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
