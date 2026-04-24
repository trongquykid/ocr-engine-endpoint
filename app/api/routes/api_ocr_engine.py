import logging
from fastapi import APIRouter, Request
from app.helpers.exception_handler import BaseHTTPException
from app.schemas.sche_base import DataResponse
from pydantic import BaseModel, Field
from PIL import Image

from app.services.ocr_text.ocr_text_api import decode_base64_to_image, ocr_recognize_from_image, ocr_recognize_to_text
from app.services.ocr_text.surya.input.process_image_input import process_image_v2

router = APIRouter()

logger = logging.getLogger(__name__)

class OCRBase64Request(BaseModel):
    image_base64: str
    filePath: str

@router.post("/ocr", response_model=DataResponse[dict])
async def run_ocr_base64(request: Request, body: OCRBase64Request):
    try:
        models = request.app.state.models
        det_predictor = models["det"]
        rec_predictor = models["rec"]
        table_rec_predictor = models["table"]
        layout_predictor = models["layout"]

        image = decode_base64_to_image(body.image_base64)
        #image = process_image_v2(image)
        #image = Image.fromarray(image)
        
        result = ocr_recognize_from_image(
            image=image,
            filePath=body.filePath,
            det_predictor=det_predictor,
            rec_predictor=rec_predictor,
            table_rec_predictor=table_rec_predictor,
            layout_predictor=layout_predictor
        )
        return DataResponse().success_response(data=result)
    except Exception as e:
        logger.exception("OCR base64 failed")
        raise BaseHTTPException(
            status_code=500,
            error_message=str(e)
        )
    
@router.post("/ocr-test", response_model=DataResponse[dict])
async def run_ocr_base64_usecase(request: Request, body: OCRBase64Request):
    try:
        models = request.app.state.models
        det_predictor = models["det"]
        rec_predictor = models["rec"]
        table_rec_predictor = models["table"]
        layout_predictor = models["layout"]

        image = decode_base64_to_image(body.image_base64)
        #image = process_image_v2(image)
        #image = Image.fromarray(image)
        
        result = ocr_recognize_to_text(
            image=image,
            filePath=body.filePath,
            det_predictor=det_predictor,
            rec_predictor=rec_predictor,
            table_rec_predictor=table_rec_predictor,
            layout_predictor=layout_predictor
        )
        return DataResponse().success_response(data=result)
    except Exception as e:
        logger.exception("OCR base64 failed")
        raise BaseHTTPException(
            status_code=500,
            error_message=str(e)
        )