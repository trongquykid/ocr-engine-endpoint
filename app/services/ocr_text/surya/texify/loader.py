from typing import Optional

import torch

from app.services.ocr_text.surya.common.load import ModelLoader
from app.services.ocr_text.surya.settings import settings
from app.services.ocr_text.surya.texify.model.config import TexifyConfig, TexifyDecoderConfig, TexifyEncoderConfig

from app.services.ocr_text.surya.texify.model.encoderdecoder import TexifyModel
from app.services.ocr_text.surya.texify.processor import TexifyProcessor


class TexifyModelLoader(ModelLoader):
    def __init__(self, checkpoint: Optional[str] = None):
        super().__init__(checkpoint)

        if self.checkpoint is None:
            self.checkpoint = settings.TEXIFY_MODEL_CHECKPOINT

    def model(
            self,
            device=settings.TORCH_DEVICE_MODEL,
            dtype=settings.MODEL_DTYPE
    ) -> TexifyModel:
        if device is None:
            device = settings.TORCH_DEVICE_MODEL
        if dtype is None:
            dtype = settings.MODEL_DTYPE

        config = TexifyConfig.from_pretrained(self.checkpoint)
        decoder_config = config.decoder
        decoder = TexifyDecoderConfig(**decoder_config)
        config.decoder = decoder

        encoder_config = config.encoder
        encoder = TexifyEncoderConfig(**encoder_config)
        config.encoder = encoder

        model = TexifyModel.from_pretrained(self.checkpoint, config=config, torch_dtype=dtype)

        model = model.to(device)
        model = model.eval()

        if settings.COMPILE_ALL or settings.COMPILE_TEXIFY:
            torch.set_float32_matmul_precision('high')
            torch._dynamo.config.cache_size_limit = 16
            torch._dynamo.config.suppress_errors = False

            print(f"Compiling texify model {self.checkpoint} on device {device} with dtype {dtype}")
            compile_args = {'backend': 'openxla'} if device == 'xla' else {}
            model.encoder = torch.compile(model.encoder, **compile_args)
            model.decoder = torch.compile(model.decoder, **compile_args)

        print(f"Loaded texify model {self.checkpoint} on device {device} with dtype {dtype}")
        return model

    def processor(self) -> TexifyProcessor:
        return TexifyProcessor(self.checkpoint)