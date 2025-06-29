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
    folder_name = os.path.basename(filepath).split(".")[0]

    result_path = os.path.abspath(os.path.join(output_dir, folder_name))
    os.makedirs(result_path, exist_ok=True)

    return images, names, highres_images, result_path

def ocr_recognize(input_path, reqCode, det_predictor, rec_predictor, layout_predictor, table_rec_predictor):
    images, names, highres_images, result_path = load(input_path)

    image_langs = [None] * len(images)

    # table_predictions = 
    table_predictions = table_recognition(images, names, highres_images, layout_predictor, table_rec_predictor)

    start = time.time()
    predictions_by_image = rec_predictor(
        images,
        image_langs,
        det_predictor=det_predictor,
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
    
    # for name, pred, image in zip(names, predictions_by_image, images):
    #     out_pred = pred.model_dump()
    #     out_pred["page"] = len(out_preds[name]) + 1
    #     out_preds[name].append(out_pred)
    #     if table_predictions:
    #         # print(f"Out_pred: {out_pred}")
    #         count_cell = 0
    #         count_row = 0
    #         for i, bboxes_cell in enumerate(table_predictions):
    #             for bbox in bboxes_cell['cells']:
    #                 combined_text = merge_ocr_ordered(bbox["bbox"], out_pred["text_lines"], count_cell, i)
    #                 count_cell += 1
                    
    #         bbox_col = [l['bbox'] for l in combined_text]
    #         conf_col = [l['confidence'] for l in combined_text]
    #         image_cp = copy.deepcopy(page_image)
    #         bbox_image = draw_bboxes_on_image(bboxes=bbox_col, image=image_cp, confidences=conf_col)
    #         file_minio = save_image_api(f"ocr/ecm/{reqCode}", bbox_image, f"bbox_{name}.png")
    #         # bbox_image.save(os.path.join(result_path, f"bbox_conf_page_table.png"))

    #         for i, bboxes_cell in enumerate(table_predictions):
    #             for bbox in bboxes_cell['rows']:
    #                 combined_text = merge_ocr_ordered(bbox["bbox"], out_pred["text_lines"], count_row, i)
    #                 count_row += 1
    #         return sorted_cells(combined_text), file_minio, file_minio_detect
    #     else:
    #         bbox_col = [l['bbox'] for l in out_pred["text_lines"]]
    #         conf_col = [l['confidence'] for l in out_pred["text_lines"]]
    #         image_cp = copy.deepcopy(page_image)
    #         bbox_image = draw_bboxes_on_image(bboxes=bbox_col, image=image_cp, confidences=conf_col)
    #         file_minio = save_image_api(f"ocr/ecm/{reqCode}", bbox_image, f"bbox_{name}.png")
    #         # return combined_text
    #         return out_pred["text_lines"], file_minio, file_minio_detect
    ocr_out_preds = dict()

    for name, pred, image in zip(names, predictions_by_image, images):
        out_pred = pred.model_dump()
        out_pred["page"] = len(out_preds[name]) + 1
        out_preds[name].append(out_pred)
        if table_predictions:
            # print(f"Out_pred: {out_pred}")
            count_cell = 0
            count_row = 0
            lst_bbox_row = []
            for i, bboxes_cell in enumerate(table_predictions):
                for bbox in bboxes_cell['cells']:
                    combined_text = merge_ocr_ordered(bbox["bbox"], out_pred["text_lines"], count_cell, i)
                    count_cell += 1
                for bbox_row in bboxes_cell['rows']:
                    lst_bbox_row.append(bbox_row)

            ocr_out_preds['cells'] = combined_text
            ocr_out_preds['rows'] = lst_bbox_row
                    
            bbox_col = [l['bbox'] for l in combined_text]
            conf_col = [l['confidence'] for l in combined_text]
            image_cp = copy.deepcopy(page_image)
            bbox_image = draw_bboxes_on_image(bboxes=bbox_col, image=image_cp, confidences=conf_col)
            file_minio = save_image_api(f"ocr/ecm/{reqCode}", bbox_image, f"bbox_{name}.png")
            # bbox_image.save(os.path.join(result_path, f"bbox_conf_page_table.png"))

            # for i, bboxes_cell in enumerate(table_predictions):
            #     for bbox in bboxes_cell['rows']:
            #         combined_text = merge_ocr_ordered(bbox["bbox"], out_pred["text_lines"], count_row, i)
            #         count_row += 1
            # return sorted_cells(combined_text), file_minio, file_minio_detect
            return ocr_out_preds, file_minio, file_minio_detect
        
        else:
            bbox_col = [l['bbox'] for l in out_pred["text_lines"]]
            conf_col = [l['confidence'] for l in out_pred["text_lines"]]
            image_cp = copy.deepcopy(page_image)
            bbox_image = draw_bboxes_on_image(bboxes=bbox_col, image=image_cp, confidences=conf_col)
            file_minio = save_image_api(f"ocr/ecm/{reqCode}", bbox_image, f"bbox_{name}.png")
            ocr_out_preds['cells'] = out_pred["text_lines"]
            # return combined_text
            return ocr_out_preds, file_minio, file_minio_detect
    
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
    
