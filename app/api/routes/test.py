from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.helpers import kafka_helper
from pydantic import BaseModel
import logging, logging.config
import datetime

from app.models.model_book import Book, BookUpdate

from app.schemas.sche_base import DataResponse

# from app.services.detection_service.detect_text import TextDetectionService
# from app.services.recognition_service.recognition_text import TextRecognitionService
from typing import List
from collections import defaultdict

router = APIRouter()
logger = logging.getLogger(__name__)

class TestReq(BaseModel):
    key: str
    channelId: str
    message: str

class ImagePathRequest(BaseModel):
    image_path: str

class FileRequest(BaseModel):
    image_path: str
    file: List

@router.post("/hello")
def hello_func():
    return "Hello World"

@router.get("/push-message")
async def test_kafka(request: Request):
    try:

        # item = {
        #     "name": "ocr management system",
        #     "project": "python app"
        # }
        # db = request.app.state.db
        # collection = db['test']
        # # Insert into mongodb
        # result = collection.insert_one(item)
        # print(f"result: {result}")
        # if not result.inserted_id:
        #     raise HTTPException(status_code=500, detail="Failed to insert DB")
        
        data = {
            "key" : "1",
            "aggregate_type": "DOCUMENT",
            "aggregate_id": "55b9e03c-eeb5-4405-85a8-8797f1356408",
            "request_code": "AI-00000069",
            "source": "OPS",
            "payload": [
                {
                "file_name": "12a.png",
                "file_path": "file_saved/scan_Mo_tai_khoan_KHTC_page-0001.jpg"
                }
            ],
            "timestamp": "1727692766.8779638"
        }

        header = {
            "id": "",
            "event_type": "CREATED",
            }

        await kafka_helper.pushMessage(topic="ocr-detection", key=data["key"], mess=data, header=header)
        return DataResponse().custom_response(code=str(status.HTTP_200_OK),
                                                    message="Push message kafka success", data=None)
    except Exception as error:
        mess_vn = "Có lỗi trong quá trình kết nối"
        logger.error(f"Internal server error: ({status.HTTP_500_INTERNAL_SERVER_ERROR}) - {str(error)} at {datetime.datetime.now()}")
        dataRes = DataResponse().custom_response(code=str(status.HTTP_500_INTERNAL_SERVER_ERROR),
                                                    message=mess_vn, data=None).model_dump_json()
        logger.info(f"dataRes: {dataRes}")
        await kafka_helper.pushMessage( topic="test",
                                        key=data["key"],
                                        mess=dataRes.__str__(), header=None)
        
@router.post("/create-book", response_description="Create a new book", status_code=status.HTTP_201_CREATED, response_model=DataResponse)
def create_book(request: Request, book: Book = Body(...)):
    book = jsonable_encoder(book)
    new_book = request.app.database["books"].insert_one(book)
    created_book = request.app.database["books"].find_one(
        {"_id": new_book.inserted_id}
    )
    return DataResponse().custom_response(code="200", data=created_book, message="Thanh cong")
