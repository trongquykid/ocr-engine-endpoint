import logging
from fastapi import FastAPI
from app.common import config
from pymongo import MongoClient

logger = logging.getLogger(__name__)

async def init_db(app: FastAPI):
    app.client = MongoClient(config.settings.DATABASE_URL)
    app.database = app.client[config.settings.MONGODB_DATABASE]
    logger.info(f"connected db: {app.database}")
    print(f"connected db: {app.database['users']}")