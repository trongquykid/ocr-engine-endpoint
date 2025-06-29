import os
import click
import json
import time
import copy
from collections import defaultdict
from io import BytesIO
import requests
from PIL import Image
import base64

from app.services.ocr_text.table_recognize import table_recognition
from app.services.ocr_text.surya.settings import settings

def decode_base64_to_image(base64_str: str) -> Image.Image:
    if "," in base64_str:
        _, base64_data = base64_str.split(",", 1)
    else:
        base64_data = base64_str
    image_bytes = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    return image

def get_name_from_path(path):
    return os.path.basename(path).split(".")[0]

def ocr_recognize_from_image(
    image: Image.Image,
    reqCode: str,
    filePath: str,
    det_predictor,
    rec_predictor,
    table_rec_predictor,
    layout_predictor
):
    images = [image]
    names = [get_name_from_path(filePath)]
    highres_images = [image]  # tùy thuộc vào pipeline của bạn

    image_langs = [None]

    table_predictions = table_recognition(
        images, names, highres_images, reqCode, layout_predictor, table_rec_predictor
    )

    predictions_by_image = rec_predictor(
        images,
        image_langs,
        det_predictor=det_predictor,
        table_predictions=table_predictions,
        highres_images=highres_images
    )

    out_preds = defaultdict(list)
    ocr_out_preds_all = dict()

    for name, pred, image in zip(names, predictions_by_image, images):
        out_pred = pred.model_dump()
        out_pred["page"] = len(out_preds[name]) + 1
        out_preds[name].append(out_pred)

        ocr_out_preds_all['lines'] = out_pred["text_lines"]
        if table_predictions:
            ocr_out_preds_all['tables'] = table_predictions

        return ocr_out_preds_all
        
def save_image_api(file_path, image, name_image):
    print('file_path', file_path)
    image_file = BytesIO()
    image.save(image_file, format='PNG')
    img_byte_arr = image_file.getvalue()
    files = {'file': (name_image, img_byte_arr, 'multipart/form-data')}
    data = {'path_file': file_path}
    url = f"{settings.URL_FILESTORAGE}/upload-file-minio"
    response_save_image = requests.post(url, data=data, files=files)
    response_data = response_save_image.json()
    return response_data['data']
    
