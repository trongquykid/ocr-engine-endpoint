import os
import click
import json
import time
import copy
from collections import defaultdict
from io import BytesIO
import requests

from app.services.ocr_text.table_recognize import table_recognition
from app.services.ocr_text.process_data import merge_text, sorted_cells, merge_ocr_ordered
from app.services.ocr_text.surya.debug.text import draw_text_on_image
from app.services.ocr_text.surya.debug.draw import draw_bboxes_on_image
from app.services.ocr_text.surya.input.load import load_image
from app.services.ocr_text.surya.settings import settings

def load(filepath):
    output_dir = os.path.join(settings.RESULT_DIR, "surya")
    
    images, names = load_image(filepath)
    highres_images = images

    return images, names, highres_images

def ocr_recognize(input_path, reqCode, det_predictor, rec_predictor, layout_predictor, table_rec_predictor):
    images, names, highres_images = load(input_path)

    image_langs = [None] * len(images)

    # table_predictions = 
    table_predictions = table_recognition(images, names, highres_images, reqCode, layout_predictor, table_rec_predictor)

    start = time.time()
    predictions_by_image = rec_predictor(
        images,
        image_langs,
        det_predictor=det_predictor,
        table_predictions=table_predictions,
        highres_images=highres_images
    )

    for idx, (name, image, pred, langs) in enumerate(zip(names, images, predictions_by_image, image_langs)):
        image_or = copy.deepcopy(image)
        bboxes = [l.bbox for l in pred.text_lines]
        pred_text = [l.text for l in pred.text_lines]
        pred_conf = [l.confidence for l in pred.text_lines]
        # print(table_predictions)

        page_image = draw_text_on_image(bboxes, pred_text, image.size, langs)
        bbox_image_detect = draw_bboxes_on_image(bboxes=bboxes, image=image_or, confidences=pred_conf)
        file_minio_detect = save_image_api(f"ocr/ecm/{reqCode}", bbox_image_detect, f"bbox_detect_{name}.png")

    out_preds = defaultdict(list)
    
    ocr_out_preds_all = dict()
    ocr_out_preds = dict()

    for name, pred, image in zip(names, predictions_by_image, images):
        out_pred = pred.model_dump()
        out_pred["page"] = len(out_preds[name]) + 1
        out_preds[name].append(out_pred)

        ocr_out_preds_all['lines'] = out_pred["text_lines"]
        if table_predictions:
            # print(f"Out_pred: {out_pred}")
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
    
