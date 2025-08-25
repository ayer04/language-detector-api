# app/auth.py
import os
from typing import Optional, Set
from fastapi import Header, HTTPException, status

def _load_keys() -> Set[str]:
    raw = os.getenv("API_KEYS", "").strip()
    return {k.strip() for k in raw.split(",") if k.strip()} or {"dev"}

API_KEYS = _load_keys()

async def api_key_auth(
    x_api_key: Optional[str] = Header(None),
    x_rapidapi_key: Optional[str] = Header(None),
):
    key = (x_api_key or x_rapidapi_key or "").strip()
    if not key or key not in API_KEYS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key")
    return key
