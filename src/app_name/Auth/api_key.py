import os

from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException

# API Key validation:

api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_scheme)):

    if api_key == os.getenv("API_KEY"):
        return {
          "api_key_user": True,
          "api_key": api_key
        }
    raise HTTPException(status_code=401, detail="Invalid API Key")