import os
from typing import Callable, Dict, Optional

import torch
from dotenv import find_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings
from app.common.config import settings as st

class Settings(BaseSettings):
    # General
    TORCH_DEVICE: Optional[str] = st.TORCH_DEVICE
    IMAGE_DPI: int = st.IMAGE_DPI # Used for detection, layout, reading order
    IMAGE_DPI_HIGHRES: int = st.IMAGE_DPI_HIGHRES  # Used for OCR, table rec
    IN_STREAMLIT: bool = st.IN_STREAMLIT # Whether we're running in streamlit
    ENABLE_EFFICIENT_ATTENTION: bool = st.ENABLE_EFFICIENT_ATTENTION # Usually keep True, but if you get CUDA errors, setting to False can help
    ENABLE_CUDNN_ATTENTION: bool = st.ENABLE_CUDNN_ATTENTION # Causes issues on many systems when set to True, but can improve performance on certain GPUs
    FLATTEN_PDF: bool = st.FLATTEN_PDF # Flatten PDFs by merging form fields before processing
    DISABLE_TQDM: bool = st.DISABLE_TQDM # Disable tqdm progress bars
    S3_BASE_URL: str = st.S3_BASE_URL
    PARALLEL_DOWNLOAD_WORKERS: int = st.PARALLEL_DOWNLOAD_WORKERS # Number of workers for parallel model downloads

    # Paths
    DATA_DIR: str = st.DATA_DIR
    RESULT_DIR: str = st.RESULT_DIR
    BASE_DIR: str = st.BASE_DIR
    FONT_DIR: str = st.FONT_DIR

    @computed_field
    def TORCH_DEVICE_MODEL(self) -> str:
        if self.TORCH_DEVICE is not None:
            return self.TORCH_DEVICE

        if torch.cuda.is_available():
            return "cuda"

        if torch.backends.mps.is_available():
            return "mps"

        try:
            import torch_xla
            if len(torch_xla.devices()) > 0:
                return "xla"
        except:
            pass

        return "cpu"

    # Text detection
    DETECTOR_BATCH_SIZE: Optional[int] = st.DETECTOR_BATCH_SIZE # Defaults to 2 for CPU/MPS, 32 otherwise
    DETECTOR_MODEL_CHECKPOINT: str = st.DETECTOR_MODEL_CHECKPOINT
    DETECTOR_BENCH_DATASET_NAME: str = st.DETECTOR_BENCH_DATASET_NAME
    DETECTOR_IMAGE_CHUNK_HEIGHT: int = st.DETECTOR_IMAGE_CHUNK_HEIGHT # Height at which to slice images vertically
    DETECTOR_TEXT_THRESHOLD: float = st.DETECTOR_TEXT_THRESHOLD # Threshold for text detection (above this is considered text)
    DETECTOR_BLANK_THRESHOLD: float = st.DETECTOR_BLANK_THRESHOLD # Threshold for blank space (below this is considered blank)
    DETECTOR_POSTPROCESSING_CPU_WORKERS: int = st.DETECTOR_POSTPROCESSING_CPU_WORKERS # Number of workers for postprocessing
    DETECTOR_MIN_PARALLEL_THRESH: int = st.DETECTOR_MIN_PARALLEL_THRESH # Minimum number of images before we parallelize
    DETECTOR_BOX_Y_EXPAND_MARGIN: float = st.DETECTOR_BOX_Y_EXPAND_MARGIN  #Margin by which to expand detected boxes vertically
    COMPILE_DETECTOR: bool = st.COMPILE_DETECTOR

    # Text recognition
    RECOGNITION_MODEL_CHECKPOINT: str = st.RECOGNITION_MODEL_CHECKPOINT
    RECOGNITION_MAX_TOKENS: int = st.RECOGNITION_MAX_TOKENS
    RECOGNITION_BATCH_SIZE: Optional[int] = st.RECOGNITION_BATCH_SIZE # Defaults to 8 for CPU/MPS, 256 otherwise
    RECOGNITION_IMAGE_SIZE: Dict = st.RECOGNITION_IMAGE_SIZE
    RECOGNITION_RENDER_FONTS: Dict[str, str] = st.RECOGNITION_RENDER_FONTS
    RECOGNITION_FONT_DL_BASE: str = st.RECOGNITION_FONT_DL_BASE
    RECOGNITION_BENCH_DATASET_NAME: str = st.RECOGNITION_BENCH_DATASET_NAME
    RECOGNITION_PAD_VALUE: int = st.RECOGNITION_PAD_VALUE
    COMPILE_RECOGNITION: bool = st.COMPILE_RECOGNITION # Static cache for torch compile

    # Layout
    LAYOUT_MODEL_CHECKPOINT: str = st.LAYOUT_MODEL_CHECKPOINT
    LAYOUT_IMAGE_SIZE: Dict = st.LAYOUT_IMAGE_SIZE
    LAYOUT_SLICE_MIN: Dict = st.LAYOUT_SLICE_MIN # When to start slicing images
    LAYOUT_SLICE_SIZE: Dict = st.LAYOUT_SLICE_SIZE # Size of slices
    LAYOUT_BATCH_SIZE: Optional[int] = st.LAYOUT_BATCH_SIZE
    LAYOUT_BENCH_DATASET_NAME: str = st.LAYOUT_BENCH_DATASET_NAME
    LAYOUT_MAX_BOXES: int = st.LAYOUT_MAX_BOXES
    COMPILE_LAYOUT: bool = st.COMPILE_LAYOUT
    ORDER_BENCH_DATASET_NAME: str = st.ORDER_BENCH_DATASET_NAME

    # Table Rec
    TABLE_REC_MODEL_CHECKPOINT: str = st.TABLE_REC_MODEL_CHECKPOINT
    TABLE_REC_IMAGE_SIZE: Dict = st.TABLE_REC_IMAGE_SIZE
    TABLE_REC_MAX_BOXES: int = st.TABLE_REC_MAX_BOXES
    TABLE_REC_BATCH_SIZE: Optional[int] = st.TABLE_REC_BATCH_SIZE
    TABLE_REC_BENCH_DATASET_NAME: str = st.TABLE_REC_BENCH_DATASET_NAME
    COMPILE_TABLE_REC: bool = st.COMPILE_TABLE_REC

    # Tesseract (for benchmarks only)
    TESSDATA_PREFIX: Optional[str] = None

    URL_FILESTORAGE: str = st.URL_FILESTORAGE
    
    COMPILE_ALL: bool = False

    @computed_field
    def DETECTOR_STATIC_CACHE(self) -> bool:
        return self.COMPILE_ALL or self.COMPILE_DETECTOR or self.TORCH_DEVICE_MODEL == "xla" # We need to static cache and pad to batch size for XLA, since it will recompile otherwise

    @computed_field
    def RECOGNITION_STATIC_CACHE(self) -> bool:
        return self.COMPILE_ALL or self.COMPILE_RECOGNITION or self.TORCH_DEVICE_MODEL == "xla"

    @computed_field
    def LAYOUT_STATIC_CACHE(self) -> bool:
        return self.COMPILE_ALL or self.COMPILE_LAYOUT or self.TORCH_DEVICE_MODEL == "xla"

    @computed_field
    def TABLE_REC_STATIC_CACHE(self) -> bool:
        return self.COMPILE_ALL or self.COMPILE_TABLE_REC or self.TORCH_DEVICE_MODEL == "xla"

    @computed_field
    def MODEL_DTYPE(self) -> torch.dtype:
        if self.TORCH_DEVICE_MODEL == "cpu":
            return torch.float32
        if self.TORCH_DEVICE_MODEL == "xla":
            return torch.bfloat16
        return torch.float32

    @computed_field
    def INFERENCE_MODE(self) -> Callable:
        if self.TORCH_DEVICE_MODEL == "xla":
            return torch.no_grad
        return torch.inference_mode

    class Config:
        env_file = find_dotenv("local.env")
        extra = "ignore"


settings = Settings()
