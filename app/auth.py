
import os
from typing import Optional, Set
from fastapi import Header, HTTPException, status

def _load_keys() -> Set[str]:
    raw = os.getenv("API_KEYS", "").strip()
    if not raw:
        # Dev-Mode: Standard-Key 'dev' ist erlaubt
        return {"dev"}
    return {k.strip() for k in raw.split(",") if k.strip()}

API_KEYS = _load_keys()

async def api_key_auth(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )
    return x_api_key
