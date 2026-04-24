from paddleocr import PaddleOCR
import cv2
from app.common.config import settings

ocr = PaddleOCR(lang=settings.LANG_PPOCR ,rec_algorithm=settings.REC_ALGORITHM, use_gpu=settings.MODEL_DEVICE)

def perform_ocr(image):
    ocr_res = ocr.ocr(image, cls=False, det=False)
    return ocr_res[0][0][0], ocr_res[0][0][1]