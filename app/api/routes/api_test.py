from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from app.helpers import kafka_helper
from pydantic import BaseModel
import logging, logging.config
import datetime

from app.models.model_book import Book, BookUpdate
from app.common.config import settings
from app.schemas.sche_base import DataResponse
from fastapi import File, UploadFile
import base64
import datetime



router = APIRouter()
logger = logging.getLogger(__name__)

class TestReq(BaseModel):
    key: str
    channelId: str
    message: str

@router.post("/hello")
def hello_func():
    return "Hello World"

@router.post("/push-message")
async def test_kafka(request: Request):
    try:
        # file_content = await file.re 

        data = {
            "aggregate_type": "DOCUMENT",
            "aggregate_id": "55b9e03c-eeb5-4405-85a8-8797f1356408",
            "request_code": "AI-00000069",
            "source": "OPS",
            "payload": [
                {
                "file_name": "12a.png",
                "file_path": "./file_storage/97c85bf9-6df5-445c-9329-de42e9c2c777.png"
                }
            ],
            "timestamp": "1727692766.8779638"
        }
     
        
        await kafka_helper.pushMessage(topic=settings.KAFKA_TOPIC_PREPROCESSING, key=data["aggregate_id"],header=None ,mess=data)
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