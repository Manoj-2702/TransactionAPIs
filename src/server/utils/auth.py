import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import pandas as pd
from ..database import verify_key


API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)):
  if not verify_key(api_key):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Invalid API Key")
