import logging

from fastapi import APIRouter, Depends

from app_name.Auth.api_key import get_api_key

test_router = APIRouter()
logger = logging.getLogger("app_logger") # Configure inside src/app/__main__.py

@test_router.get("/test")
async def test(api_key: dict = Depends(get_api_key)):

    logger.info(f"[{api_key['api_key']}] -  Received Request at /test")

    return {"message": "Hello World"}