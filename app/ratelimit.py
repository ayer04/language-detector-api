
import os
import time
from typing import Tuple, Optional
from fastapi import HTTPException, status
try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # optional dependency


class RateLimiter:
    """
    Simpler Rate-Limiter. Nutzt Redis, wenn REDIS_URL gesetzt ist, sonst In-Memory.
    Limit ist pro API-Key pro Minute.
    """
    def __init__(self, limit_per_minute: int = 60):
        self.limit = int(os.getenv("LIMIT_PER_MINUTE", str(limit_per_minute)))
        self._mem = {}
        self._redis = None
        url = os.getenv("REDIS_URL", "").strip()
        if url and redis is not None:
            try:
                self._redis = redis.Redis.from_url(url, decode_responses=True)
            except Exception:
                self._redis = None

    def _window_key(self, api_key: str) -> Tuple[str, int]:
        now = int(time.time())
        window = now // 60  # Minutenfenster
        return f"rl:{api_key}:{window}", window

    def check(self, api_key: str):
        if self.limit <= 0:
            return  # deaktiviert
        key, window = self._window_key(api_key)
        if self._redis:
            # Redis-Variante
            try:
                pipe = self._redis.pipeline()
                pipe.incr(key)
                pipe.expire(key, 120)
                current = pipe.execute()[0]
            except Exception:
                # Fallback auf Memory
                current = None
                self._redis = None

            if current is not None:
                if int(current) > self.limit:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded",
                    )
                return

        # In-Memory
        count, win = self._mem.get(key, (0, window))
        if win != window:
            count = 0
            win = window
        count += 1
        self._mem[key] = (count, win)
        if count > self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

    def headers(self, api_key: str) -> dict:
        # Simple Header-Angaben (keine exakte Restanzahl im Memory-Fallback)
        return {
            "X-RateLimit-Limit": str(self.limit),
        }
