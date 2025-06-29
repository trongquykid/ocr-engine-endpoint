import logging, logging.config

from fastapi import APIRouter

from app.schemas.sche_base import ResponseSchemaBase
router = APIRouter()
logger = logging.getLogger(__name__)



@router.get("", response_model=ResponseSchemaBase)
async def get():
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
    logger.debug("Health check success")
    return {"message": "Health check success"}