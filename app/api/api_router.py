from fastapi import APIRouter

from app.api.routes import test, api_healthcheck, api_test, api_ocr_engine

router = APIRouter()

router.include_router(test.router, tags=["test"])
router.include_router(api_healthcheck.router, tags=["health-check"], prefix="/healthcheck")
router.include_router(api_test.router, tags=["api_test"], prefix="/api_test")
router.include_router(api_ocr_engine.router, tags=["ocr"], prefix="/surya")