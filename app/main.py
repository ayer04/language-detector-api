
import os
from typing import List
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware

from .schemas import TextIn, BatchIn, DetectOut, AltCandidate
from .auth import api_key_auth
from .ratelimit import RateLimiter
from .detector import Detector
from .utils import iso3_from_alpha2

APP_NAME = os.getenv("APP_NAME", "Lightning Language Detector")
app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="Schnelle Language Detection API (176+ Sprachen, FastAPI).",
)

# CORS (optional liberal)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = Detector()
limiter = RateLimiter(limit_per_minute=int(os.getenv("LIMIT_PER_MINUTE", "120")))

@app.get("/health")
def health():
    return {"status": "ok", "engine": detector.engine_name}

@app.post("/detect", response_model=DetectOut, tags=["detect"])
def detect(payload: TextIn, api_key: str = Depends(api_key_auth)):
    limiter.check(api_key)
    raw = detector.detect(payload.text)
    # Enrich iso639_3
    raw["iso639_3"] = iso3_from_alpha2(raw["language"])
    # Set rate headers
    headers = limiter.headers(api_key)
    resp = DetectOut(**raw)
    return Response(content=resp.json(), media_type="application/json", headers=headers)

@app.post("/detect/batch", response_model=List[DetectOut], tags=["detect"])
def detect_batch(payload: BatchIn, api_key: str = Depends(api_key_auth)):
    limiter.check(api_key)
    results = detector.detect_batch(payload.items)
    for r in results:
        r["iso639_3"] = iso3_from_alpha2(r["language"])
    headers = limiter.headers(api_key)
    data = [DetectOut(**r).dict() for r in results]
    from json import dumps
    return Response(content=dumps(data), media_type="application/json", headers=headers)
