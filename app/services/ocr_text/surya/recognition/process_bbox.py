def bbox_to_polygon(bbox):
    x_min, y_min, x_max, y_max = map(int, bbox)
    return [
        [x_min, y_min],
        [x_max, y_min],
        [x_max, y_max],
        [x_min, y_max]
    ]

def split_bbox_if_cut(bbox_detect, bbox_col):
    x1, y1, x2, y2 = bbox_detect
    x_c1, y_c1, x_c2, y_c2 = bbox_col
    results = []

    # Cắt theo chiều ngang (x) nếu bbox_detect nằm trọn theo chiều dọc của bbox_col
    if y_c1 <= y1 <= y_c2 and y_c1 <= y2 <= y_c2:
        if x1 < x_c1 < x2:
            if x2 - x_c1 > 20 and x_c1 - x1 > 20:
                results.append([int(x1), int(y1), int(x_c1), int(y2)])
                results.append([int(x_c1), int(y1), int(x2), int(y2)])
                return results
        if x1 < x_c2 < x2:
            if x2 - x_c2 > 20 and x_c2 - x1 > 20:
                results.append([int(x1), int(y1), int(x_c2), int(y2)])
                results.append([int(x_c2), int(y1), int(x2), int(y2)])
                return results

    return [list(map(int, bbox_detect))]


def process_bbox_detect(bbox_detect_list, bbox_col_list):
    output = []
    for detect in bbox_detect_list:
        # orig_bbox = detect["bbox"]
        orig_bbox = detect.bbox

        splitted_bboxes = [orig_bbox]

        for col in bbox_col_list:
            col_bbox = col["bbox"]
            temp = []
            for b in splitted_bboxes:
                temp.extend(split_bbox_if_cut(b, col_bbox))
            splitted_bboxes = temp

        for b in splitted_bboxes:
            int_bbox = list(map(int, b))
            new_item = {
                "confidence": detect.confidence,
                "bbox": int_bbox
            }
            # if "polygon" in detect:
            if hasattr(detect, "polygon"):
                new_item["polygon"] = bbox_to_polygon(int_bbox)
            output.append(new_item)
    return output
