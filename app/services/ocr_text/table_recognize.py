from collections import defaultdict
import copy, os
from app.services.ocr_text.surya.debug.draw import draw_bboxes_on_image

from app.services.ocr_text.process_data import offset_table_bboxes
from app.services.ocr_text.surya.common.util import rescale_bbox, expand_bbox

from app.services.ocr_text.surya.settings import settings
from io import BytesIO
import requests


def table_recognition(images, names, highres_images, requestCode, layout_predictor, table_rec_predictor):

    # images, names, highres_images, result_path = load(input_path)

    pnums = []
    prev_name = None
    for i, name in enumerate(names):
        if prev_name is None or prev_name != name:
            pnums.append(0)
        else:
            pnums.append(pnums[-1] + 1)

        prev_name = name

    layout_predictions = layout_predictor(images)

    table_imgs = []
    table_counts = []
    highres_bboxes_per_page = []

    for layout_pred, img, highres_img in zip(layout_predictions, images, highres_images):

        bbox = [l.bbox for l in layout_pred.bboxes if l.label in ["Table", "TableOfContents"]]
        table_counts.append(len(bbox))

        if len(bbox) == 0:
            highres_bboxes_per_page.append([])
            continue

        page_table_imgs = []
        highres_bbox = []
        for bb in bbox:
            highres_bb = rescale_bbox(bb, img.size, highres_img.size)
            highres_bb = expand_bbox(highres_bb)
            page_table_imgs.append(highres_img.crop(highres_bb))
            highres_bbox.append(highres_bb)

        table_imgs.extend(page_table_imgs)
        highres_bboxes_per_page.append(highres_bbox)

    table_preds = table_rec_predictor(table_imgs)

    img_idx = 0
    prev_count = 0

    if sum(table_counts) == 0:
        return None
    
    table_predictions = defaultdict(list)
    for i in range(sum(table_counts)):
        while i >= prev_count + table_counts[img_idx]:
            prev_count += table_counts[img_idx]
            img_idx += 1

        pred = table_preds[i]
        orig_name = names[img_idx]
        pnum = pnums[img_idx]
        table_img = table_imgs[i]

        out_pred = pred.model_dump()
        out_pred["page"] = pnum + 1
        table_idx = i - prev_count
        out_pred["table_idx"] = table_idx
        # table_predictions[orig_name].append(out_pred)

        rows = [l.bbox for l in pred.rows]
        cols = [l.bbox for l in pred.cols]
        row_labels = [f"Row {l.row_id}" for l in pred.rows]
        col_labels = [f"Col {l.col_id}" for l in pred.cols]
        cells = [l.bbox for l in pred.cells]

        def offset_bbox(bbox, offset):
            return [
                bbox[0] + offset[0],
                bbox[1] + offset[1],
                bbox[2] + offset[0],
                bbox[3] + offset[1],
            ]

        table_bbox_list = highres_bboxes_per_page[img_idx]
        if table_idx < len(table_bbox_list):
            table_bb = table_bbox_list[table_idx]
            offset = table_bb[:2]  # x0, y0

            out_pred = offset_table_bboxes(out_pred, offset)

            offset_rows = [offset_bbox(b, offset) for b in rows]
            offset_cols = [offset_bbox(b, offset) for b in cols]
            offset_cells = [offset_bbox(b, offset) for b in cells]

            # === Vẽ trên ảnh gốc ===
            orig_highres_image = copy.deepcopy(highres_images[img_idx])

            rc_image = draw_bboxes_on_image(bboxes=offset_rows, image=orig_highres_image, labels=row_labels, label_font_size=20, color="blue")
            rc_image = draw_bboxes_on_image(bboxes=offset_cols, image=rc_image, labels=col_labels, label_font_size=20, color="red")
            # rc_image.save(os.path.join("./file_saved", f"{orig_name}_page{pnum + 1}_table{table_idx}_rc_on_orig.png"))

        table_predictions[orig_name].append(out_pred)
    # table_minio = save_image_api(f"ocr/kondor/{requestCode}", rc_image, f"{orig_name}_page{pnum + 1}_table{table_idx}_rc_on_orig.png")

    return table_predictions[orig_name]

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