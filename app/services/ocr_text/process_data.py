

def is_center_in_cell(bbox, cell):
    x1, y1, x2, y2 = bbox
    cx1, cy1, cx2, cy2 = cell
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return cx1 <= center_x <= cx2 and cy1 <= center_y <= cy2

def sorted_cells(data):
    indexed_items = sorted(
        [item for item in data if "table_index" in item],
        key=lambda x: x["table_index"]
    )

    indexed_iter = iter(indexed_items)

    result = [
        next(indexed_iter) if "table_index" in item else item
        for item in data
    ]
    return result

def merge_text(bbox_cell, ocr_result, index_cells):

    indices_to_replace = []
    texts_to_combine = []
    confidences = []

    for i, item in enumerate(ocr_result):
        if is_center_in_cell(item["bbox"], bbox_cell):
            indices_to_replace.append(i)
            texts_to_combine.append(item["text"])
            confidences.append(item["confidence"])
        
    if indices_to_replace:
        combined_text = " ".join(texts_to_combine).replace("\n", " ")
        average_conf = sum(confidences) / len(confidences)

        new_entry = {
            "text": combined_text,
            "bbox": bbox_cell,
            "confidence": average_conf,
            "table_index": index_cells
        }

        for idx in sorted(indices_to_replace, reverse=True):
            del ocr_result[idx]

        insertion_index = min(indices_to_replace)
        ocr_result.insert(insertion_index, new_entry)
    
    return ocr_result

def merge_ocr_ordered(bbox_row, ocr_result, row_index, table_index, y_threshold=10):

    def is_center_in_cell(bbox, cell):
        x1, y1, x2, y2 = bbox
        cx1, cy1, cx2, cy2 = cell
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return cx1 <= center_x <= cx2 and cy1 <= center_y <= cy2

    items_to_merge = []
    indices_to_replace = []

    for i, item in enumerate(ocr_result):
        if is_center_in_cell(item["bbox"], bbox_row):
            items_to_merge.append(item)
            indices_to_replace.append(i)

    if items_to_merge:

        lines = []
        for item in items_to_merge:
            y_min = item["bbox"][1]
            inserted = False
            for line in lines:
                if abs(line[0]["bbox"][1] - y_min) < y_threshold:
                    line.append(item)
                    inserted = True
                    break
            if not inserted:
                lines.append([item])

        for line in lines:
            line.sort(key=lambda x: x["bbox"][0])  # trái sang phải

        lines.sort(key=lambda line: min(x["bbox"][1] for x in line))  # trên xuống dưới

        sorted_items = [item for line in lines for item in line]
        texts_to_combine = [item["text"].replace("\n", " ") for item in sorted_items]
        confidences = [item["confidence"] for item in sorted_items]

        combined_text = " ".join(texts_to_combine)
        average_conf = sum(confidences) / len(confidences)

        new_entry = {
            "text": combined_text,
            "bbox": bbox_row,
            "confidence": average_conf,
            "row_index": row_index,
            "table_index": table_index
        }

        for idx in sorted(indices_to_replace, reverse=True):
            del ocr_result[idx]

        insertion_index = min(indices_to_replace)
        ocr_result.insert(insertion_index, new_entry)

    else:
        new_entry = {
            "text": " ",
            "bbox": bbox_row,
            "confidence": 0.9,
            "row_index": row_index,
            "table_index": table_index
        }
        ocr_result.append(new_entry)

    return ocr_result

def merge_ocr_rows_ordered(bbox_row, ocr_result, row_index, table_index, y_threshold=10):

    def is_center_in_cell(bbox, cell):
        x1, y1, x2, y2 = bbox
        cx1, cy1, cx2, cy2 = cell
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return cx1 <= center_x <= cx2 and cy1 <= center_y <= cy2

    items_to_merge = []
    indices_to_replace = []

    for i, item in enumerate(ocr_result):
        if is_center_in_cell(item["bbox"], bbox_row):
            items_to_merge.append(item)
            indices_to_replace.append(i)

    if items_to_merge:

        lines = []
        for item in items_to_merge:
            y_min = item["bbox"][1]
            inserted = False
            for line in lines:
                if abs(line[0]["bbox"][1] - y_min) < y_threshold:
                    line.append(item)
                    inserted = True
                    break
            if not inserted:
                lines.append([item])

        for line in lines:
            line.sort(key=lambda x: x["bbox"][0])  # trái sang phải

        lines.sort(key=lambda line: min(x["bbox"][1] for x in line))  # trên xuống dưới

        sorted_items = [item for line in lines for item in line]
        texts_to_combine = [item["text"].replace("\n", " ") for item in sorted_items]
        confidences = [item["confidence"] for item in sorted_items]

        combined_text = " | ".join(texts_to_combine)
        average_conf = sum(confidences) / len(confidences)

        new_entry = {
            "text": combined_text,
            "bbox": bbox_row,
            "confidence": average_conf,
            "row_index": row_index,
            "table_index": table_index
        }

        for idx in sorted(indices_to_replace, reverse=True):
            del ocr_result[idx]

        insertion_index = min(indices_to_replace)
        ocr_result.insert(insertion_index, new_entry)

    else:
        new_entry = {
            "text": "",
            "bbox": bbox_row,
            "confidence": 0.9,
            "row_index": row_index,
            "table_index": table_index
        }
        ocr_result.append(new_entry)

    return ocr_result

def offset_table_bboxes(out_pred: dict, offset: tuple[float, float]) -> dict:
    x0, y0 = offset

    def offset_bbox(bbox):
        return [bbox[0] + x0, bbox[1] + y0, bbox[2] + x0, bbox[3] + y0]

    def offset_polygon(polygon):
        return [[x + x0, y + y0] for (x, y) in polygon]

    for section in ["cells", "rows", "cols", "unmerged_cells"]:
        if section in out_pred:
            for entry in out_pred[section]:
                if "bbox" in entry:
                    entry["bbox"] = offset_bbox(entry["bbox"])
                if "polygon" in entry:
                    entry["polygon"] = offset_polygon(entry["polygon"])

    return out_pred