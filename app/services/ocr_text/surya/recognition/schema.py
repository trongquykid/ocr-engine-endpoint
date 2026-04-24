from typing import Optional, List

from pydantic import BaseModel

from app.services.ocr_text.surya.common.polygon import PolygonBox


class TextLine(PolygonBox):
    text: str
    confidence: Optional[float] = None


class OCRResult(BaseModel):
    text_lines: List[TextLine]
    languages: List[str] | None = None
    image_bbox: List[float]
