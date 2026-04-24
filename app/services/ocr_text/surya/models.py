from typing import Dict

import torch

from app.services.ocr_text.surya.common.predictor import BasePredictor
from app.services.ocr_text.surya.detection import DetectionPredictor, InlineDetectionPredictor
from app.services.ocr_text.surya.layout import LayoutPredictor
from app.services.ocr_text.surya.ocr_error import OCRErrorPredictor
from app.services.ocr_text.surya.recognition import RecognitionPredictor
from app.services.ocr_text.surya.table_rec import TableRecPredictor
from app.services.ocr_text.surya.texify import TexifyPredictor


def load_predictors(
        device: str | torch.device | None = None,
        dtype: torch.dtype | str | None = None
) -> Dict[str, BasePredictor]:
    return {
        "layout": LayoutPredictor(device=device, dtype=dtype),
        "ocr_error": OCRErrorPredictor(device=device, dtype=dtype),
        "recognition": RecognitionPredictor(device=device, dtype=dtype),
        "detection": DetectionPredictor(device=device, dtype=dtype),
        "inline_detection": InlineDetectionPredictor(device=device, dtype=dtype),
        "texify": TexifyPredictor(device=device, dtype=dtype),
        "table_rec": TableRecPredictor(device=device, dtype=dtype)
    }