import logging
from datetime import datetime, timedelta

import httpx
from jose import jwt

from app.common.config import settings

logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE = timedelta(days=1)
limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)

async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

